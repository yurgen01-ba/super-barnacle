from __future__ import annotations

from dataclasses import asdict, dataclass
import re


PROTECTED_PHRASES = {
    "in scope of this task",
    "out of scope",
    "white label",
    "jira task",
    "info panel",
    "field scope",
    "project brain",
    "hugging face",
    "speaker diarization",
    "clean transcript",
    "raw transcript",
}

SHORT_REPLY_WORDS = {
    "ага",
    "да",
    "нет",
    "угу",
    "ок",
    "okay",
}


@dataclass
class SpeakerUtterance:
    speaker: str
    start: float
    end: float
    text: str
    word_count: int
    average_score: float | None = None


@dataclass
class BoundaryDecision:
    word_index: int
    previous_speaker: str
    proposed_speaker: str
    final_speaker: str
    gap_seconds: float
    run_words: int
    run_duration_seconds: float
    sentence_boundary: bool
    protected_phrase: bool
    accepted: bool
    reason: str


def _join_words(words: list[str]) -> str:
    text = ""

    for raw_word in words:
        word = str(raw_word or "").strip()
        if not word:
            continue

        if not text:
            text = word
        elif word[0] in ",.!?:;)]}":
            text += word
        elif text[-1] in "([{":
            text += word
        else:
            text += " " + word

    return text.strip()


def _normalize_token(value: str) -> str:
    return re.sub(
        r"[^a-zа-яё0-9]+",
        "",
        str(value or "").lower(),
    )


def _is_sentence_boundary(word: str) -> bool:
    return bool(
        re.search(
            r"[.!?…][\"')\]}]*$",
            str(word or "").strip(),
        )
    )


def _flatten_words(segments: list) -> list[dict]:
    words: list[dict] = []

    for segment_index, segment in enumerate(segments):
        segment_speaker = (
            getattr(segment, "speaker", None)
            or "SPEAKER_UNKNOWN"
        )

        for word_index, word in enumerate(
            getattr(segment, "words", []) or []
        ):
            text = str(
                getattr(word, "word", "") or ""
            ).strip()
            if not text:
                continue

            start = getattr(word, "start", None)
            end = getattr(word, "end", None)

            start_value = float(
                start
                if start is not None
                else getattr(segment, "start", 0.0)
            )
            end_value = float(
                end
                if end is not None
                else getattr(segment, "end", start_value)
            )

            words.append(
                {
                    "text": text,
                    "normalized": _normalize_token(text),
                    "start": start_value,
                    "end": end_value,
                    "score": getattr(word, "score", None),
                    "original_speaker": (
                        getattr(word, "speaker", None)
                        or segment_speaker
                    ),
                    "speaker": (
                        getattr(word, "speaker", None)
                        or segment_speaker
                    ),
                    "segment_index": segment_index,
                    "word_index_in_segment": word_index,
                }
            )

    return words


def _speaker_runs(words: list[dict]) -> list[dict]:
    runs: list[dict] = []

    for index, word in enumerate(words):
        speaker = word["speaker"]

        if runs and runs[-1]["speaker"] == speaker:
            run = runs[-1]
            run["end_index"] = index
            run["end"] = word["end"]
            run["word_count"] += 1
        else:
            runs.append(
                {
                    "speaker": speaker,
                    "start_index": index,
                    "end_index": index,
                    "start": word["start"],
                    "end": word["end"],
                    "word_count": 1,
                }
            )

    return runs


def _sentence_spans(words: list[dict]) -> list[tuple[int, int]]:
    """Return inclusive word spans for punctuation-delimited phrases."""
    spans: list[tuple[int, int]] = []
    start = 0

    for index, word in enumerate(words):
        # A punctuated short acknowledgement is a real utterance even when
        # Whisper did not put punctuation on the preceding speaker's words.
        if (
            index > start
            and word["normalized"] in SHORT_REPLY_WORDS
            and _is_sentence_boundary(word["text"])
            and word["speaker"] != words[index - 1]["speaker"]
        ):
            spans.append((start, index - 1))
            spans.append((index, index))
            start = index + 1
        elif _is_sentence_boundary(word["text"]):
            spans.append((start, index))
            start = index + 1

    if start < len(words):
        spans.append((start, len(words) - 1))

    return spans


def _dominant_speaker_for_span(
    words: list[dict],
    start: int,
    end: int,
) -> tuple[str | None, float]:
    weights: dict[str, float] = {}
    total = 0.0

    for index in range(start, end + 1):
        word = words[index]
        speaker = str(word["speaker"])
        duration = max(0.05, min(2.0, word["end"] - word["start"]))
        weights[speaker] = weights.get(speaker, 0.0) + duration
        total += duration

    if not weights or total <= 0:
        return None, 0.0

    speaker, weight = max(weights.items(), key=lambda item: item[1])
    return speaker, weight / total


def stabilize_sentence_speakers(
    words: list[dict],
    max_noise_words: int = 2,
    max_noise_seconds: float = 1.35,
    min_dominance: float = 0.60,
    context_gap_seconds: float = 1.5,
) -> tuple[list[dict], list[dict]]:
    """Remove word-level speaker flips without erasing real short replies.

    Pyannote boundaries and Whisper word timestamps have independent timing
    errors. A boundary can therefore land on the first or last word of a
    phrase. We first bridge short A-B-A islands, then use adjacent sentence
    context and duration-weighted consensus for short edge fragments.
    """
    adjustments: list[dict] = []
    spans = _sentence_spans(words)

    for span_index, (start, end) in enumerate(spans):
        if start >= end:
            continue

        # Recompute until all short A-B-A islands inside the phrase are gone.
        changed = True
        while changed:
            changed = False
            runs = [
                run
                for run in _speaker_runs(words[start:end + 1])
            ]
            for run_index in range(1, len(runs) - 1):
                previous = runs[run_index - 1]
                current = runs[run_index]
                following = runs[run_index + 1]
                duration = current["end"] - current["start"]
                if (
                    previous["speaker"] == following["speaker"]
                    and current["speaker"] != previous["speaker"]
                    and current["word_count"] <= max_noise_words
                    and duration <= max_noise_seconds
                ):
                    absolute_start = start + current["start_index"]
                    absolute_end = start + current["end_index"]
                    for index in range(absolute_start, absolute_end + 1):
                        words[index]["speaker"] = previous["speaker"]
                    adjustments.append({
                        "from_word_index": absolute_start,
                        "through_word_index": absolute_end,
                        "final_speaker": str(previous["speaker"]),
                        "reason": "bridge_short_speaker_island",
                    })
                    changed = True
                    break

        local_runs = _speaker_runs(words[start:end + 1])
        if len(local_runs) != 2:
            continue

        first, last = local_runs
        last_duration = last["end"] - last["start"]

        # If the last tiny fragment already has the speaker of the next
        # phrase, the acoustic boundary probably arrived one word too early.
        if span_index + 1 < len(spans):
            next_start, next_end = spans[span_index + 1]
            next_speaker, _ = _dominant_speaker_for_span(
                words, next_start, next_end
            )
            next_gap = max(0.0, words[next_start]["start"] - words[end]["end"])
            if (
                next_speaker == last["speaker"]
                and first["speaker"] != last["speaker"]
                and last["word_count"] <= max_noise_words
                and last_duration <= max_noise_seconds
                and next_gap <= context_gap_seconds
            ):
                absolute_start = start + last["start_index"]
                for index in range(absolute_start, end + 1):
                    words[index]["speaker"] = first["speaker"]
                adjustments.append({
                    "from_word_index": absolute_start,
                    "through_word_index": end,
                    "final_speaker": str(first["speaker"]),
                    "reason": "delay_boundary_to_sentence_end",
                })
                continue

        dominant_speaker, dominance = _dominant_speaker_for_span(words, start, end)
        if dominant_speaker is None or dominance < min_dominance:
            continue

        minority = first if first["speaker"] != dominant_speaker else last
        minority_duration = minority["end"] - minority["start"]
        if (
            minority["word_count"] <= max_noise_words
            and minority_duration <= max_noise_seconds
        ):
            absolute_start = start + minority["start_index"]
            absolute_end = start + minority["end_index"]
            for index in range(absolute_start, absolute_end + 1):
                words[index]["speaker"] = dominant_speaker
            adjustments.append({
                "from_word_index": absolute_start,
                "through_word_index": absolute_end,
                "final_speaker": str(dominant_speaker),
                "dominance": round(dominance, 3),
                "reason": "sentence_speaker_consensus",
            })

    return words, adjustments


def _protected_phrase_spans(
    words: list[dict],
) -> list[tuple[int, int, str]]:
    normalized_words = [
        word["normalized"]
        for word in words
    ]
    spans: list[tuple[int, int, str]] = []

    for phrase in PROTECTED_PHRASES:
        phrase_tokens = [
            _normalize_token(token)
            for token in phrase.split()
        ]
        size = len(phrase_tokens)

        for start in range(
            0,
            len(normalized_words) - size + 1,
        ):
            if (
                normalized_words[start:start + size]
                == phrase_tokens
            ):
                spans.append(
                    (
                        start,
                        start + size - 1,
                        phrase,
                    )
                )

    return spans


def _boundary_inside_protected_phrase(
    boundary_index: int,
    spans: list[tuple[int, int, str]],
) -> tuple[bool, str | None]:
    for start, end, phrase in spans:
        if start < boundary_index <= end:
            return True, phrase

    return False, None


def _next_run_details(
    words: list[dict],
    start_index: int,
) -> tuple[int, float]:
    if start_index >= len(words):
        return 0, 0.0

    speaker = words[start_index]["speaker"]
    end_index = start_index

    while (
        end_index + 1 < len(words)
        and words[end_index + 1]["speaker"]
        == speaker
    ):
        end_index += 1

    duration = max(
        0.0,
        words[end_index]["end"]
        - words[start_index]["start"],
    )
    return (
        end_index - start_index + 1,
        duration,
    )


def snap_mid_sentence_speaker_changes(
    words: list[dict],
    max_shift_words: int = 8,
    max_shift_seconds: float = 4.0,
) -> tuple[list[dict], list[dict]]:
    """Move premature diarization boundaries to nearby sentence endings.

    Word-level diarization often flips a speaker one or two words before the
    acoustic turn boundary. We only move a boundary forward, never invent a
    new speaker, and preserve punctuated short replies such as ``Да.``.
    """
    adjustments: list[dict] = []
    index = 1

    while index < len(words):
        previous = words[index - 1]
        current = words[index]
        if current["speaker"] == previous["speaker"]:
            index += 1
            continue
        if _is_sentence_boundary(previous["text"]):
            index += 1
            continue
        if (
            current["normalized"] in SHORT_REPLY_WORDS
            and _is_sentence_boundary(current["text"])
        ):
            index += 1
            continue

        proposed_speaker = current["speaker"]
        previous_speaker = previous["speaker"]
        run_end = index
        while (
            run_end + 1 < len(words)
            and words[run_end + 1]["speaker"] == proposed_speaker
        ):
            run_end += 1

        punctuation_index = None
        upper = min(run_end, index + max_shift_words - 1)
        for candidate in range(index, upper + 1):
            duration = words[candidate]["end"] - current["start"]
            if duration > max_shift_seconds:
                break
            if _is_sentence_boundary(words[candidate]["text"]):
                punctuation_index = candidate
                break

        if punctuation_index is None:
            index += 1
            continue

        for candidate in range(index, punctuation_index + 1):
            words[candidate]["speaker"] = previous_speaker

        adjustments.append(
            {
                "from_word_index": index,
                "through_word_index": punctuation_index,
                "previous_speaker": str(previous_speaker),
                "proposed_speaker": str(proposed_speaker),
                "reason": "snap_to_sentence_boundary",
            }
        )
        index = punctuation_index + 1

    return words, adjustments


def validate_speaker_boundaries(
    words: list[dict],
    hard_min_gap_seconds: float = 0.0,
    soft_min_gap_seconds: float = 0.0,
    min_new_run_words: int = 1,
    min_new_run_duration_seconds: float = 0.0,
) -> tuple[list[dict], list[BoundaryDecision]]:
    if len(words) < 2:
        return words, []

    protected_spans = _protected_phrase_spans(words)
    decisions: list[BoundaryDecision] = []

    for index in range(1, len(words)):
        previous = words[index - 1]
        current = words[index]

        if (
            current["speaker"]
            == previous["speaker"]
        ):
            continue

        gap = max(
            0.0,
            float(current["start"])
            - float(previous["end"]),
        )
        run_words, run_duration = _next_run_details(
            words,
            index,
        )
        sentence_boundary = _is_sentence_boundary(
            previous["text"]
        )
        protected, phrase = (
            _boundary_inside_protected_phrase(
                index,
                protected_spans,
            )
        )

        accept = True
        reason = "speaker_change_confirmed"

        if protected:
            accept = False
            reason = (
                "protected_phrase:"
                + str(phrase)
            )
        # Preserve Pyannote's word-level boundaries by default. Natural
        # conversation often contains overlap, interruptions and valid
        # one-word replies such as "Да". Those must not be reassigned to the
        # previous speaker merely because there is no acoustic pause.

        proposed_speaker = str(
            current["speaker"]
        )
        previous_speaker = str(
            previous["speaker"]
        )

        if not accept:
            current["speaker"] = (
                previous["speaker"]
            )

        decisions.append(
            BoundaryDecision(
                word_index=index,
                previous_speaker=previous_speaker,
                proposed_speaker=proposed_speaker,
                final_speaker=str(
                    current["speaker"]
                ),
                gap_seconds=round(gap, 3),
                run_words=run_words,
                run_duration_seconds=round(
                    run_duration,
                    3,
                ),
                sentence_boundary=sentence_boundary,
                protected_phrase=protected,
                accepted=accept,
                reason=reason,
            )
        )

    return words, decisions


def _merge_into_utterances(
    words: list[dict],
    max_gap_seconds: float = 1.4,
) -> list[SpeakerUtterance]:
    utterances: list[SpeakerUtterance] = []
    current: dict | None = None

    for word in words:
        speaker = str(word["speaker"])

        if current:
            gap = max(
                0.0,
                word["start"] - current["end"],
            )
        else:
            gap = 0.0

        if (
            current
            and current["speaker"] == speaker
            and gap <= max_gap_seconds
        ):
            current["end"] = max(
                current["end"],
                word["end"],
            )
            current["words"].append(
                word["text"]
            )
            if word["score"] is not None:
                current["scores"].append(
                    float(word["score"])
                )
        else:
            if current:
                utterances.append(
                    _build_utterance(current)
                )

            current = {
                "speaker": speaker,
                "start": word["start"],
                "end": word["end"],
                "words": [word["text"]],
                "scores": (
                    [float(word["score"])]
                    if word["score"] is not None
                    else []
                ),
            }

    if current:
        utterances.append(
            _build_utterance(current)
        )

    return utterances


def _build_utterance(
    value: dict,
) -> SpeakerUtterance:
    scores = value.get("scores") or []

    return SpeakerUtterance(
        speaker=str(value["speaker"]),
        start=round(
            float(value["start"]),
            3,
        ),
        end=round(
            float(value["end"]),
            3,
        ),
        text=_join_words(
            value.get("words") or []
        ),
        word_count=len(
            value.get("words") or []
        ),
        average_score=(
            round(
                sum(scores) / len(scores),
                3,
            )
            if scores
            else None
        ),
    )


def stabilize_speaker_utterances(
    segments: list,
    max_flip_seconds: float = 0.55,
    max_flip_words: int = 1,
    max_gap_seconds: float = 1.4,
) -> list[SpeakerUtterance]:
    utterances, _ = (
        stabilize_speaker_utterances_with_debug(
            segments=segments,
            max_gap_seconds=max_gap_seconds,
        )
    )
    return utterances


def stabilize_speaker_utterances_with_debug(
    segments: list,
    max_gap_seconds: float = 1.4,
    hard_min_gap_seconds: float = 0.0,
    soft_min_gap_seconds: float = 0.0,
    min_new_run_words: int = 1,
    min_new_run_duration_seconds: float = 0.0,
) -> tuple[
    list[SpeakerUtterance],
    dict,
]:
    words = _flatten_words(segments)
    original_runs = _speaker_runs(words)

    words, sentence_consensus_adjustments = (
        stabilize_sentence_speakers(words)
    )

    validated_words, decisions = (
        validate_speaker_boundaries(
            words=words,
            hard_min_gap_seconds=(
                hard_min_gap_seconds
            ),
            soft_min_gap_seconds=(
                soft_min_gap_seconds
            ),
            min_new_run_words=(
                min_new_run_words
            ),
            min_new_run_duration_seconds=(
                min_new_run_duration_seconds
            ),
        )
    )

    validated_runs = _speaker_runs(
        validated_words
    )
    utterances = _merge_into_utterances(
        validated_words,
        max_gap_seconds=max_gap_seconds,
    )

    debug = {
        "word_count": len(words),
        "original_run_count": len(
            original_runs
        ),
        "validated_run_count": len(
            validated_runs
        ),
        "utterance_count": len(
            utterances
        ),
        "accepted_boundaries": sum(
            1
            for item in decisions
            if item.accepted
        ),
        "rejected_boundaries": sum(
            1
            for item in decisions
            if not item.accepted
        ),
        "thresholds": {
            "hard_min_gap_seconds": (
                hard_min_gap_seconds
            ),
            "soft_min_gap_seconds": (
                soft_min_gap_seconds
            ),
            "min_new_run_words": (
                min_new_run_words
            ),
            "min_new_run_duration_seconds": (
                min_new_run_duration_seconds
            ),
            "max_gap_seconds": (
                max_gap_seconds
            ),
        },
        "boundary_decisions": [
            asdict(item)
            for item in decisions
        ],
        "sentence_snap_adjustments": sentence_consensus_adjustments,
        "sentence_consensus_adjustments": sentence_consensus_adjustments,
        "original_runs": original_runs,
        "validated_runs": validated_runs,
    }

    return utterances, debug


def serialize_utterances(
    utterances: list[SpeakerUtterance],
) -> list[dict]:
    return [
        asdict(item)
        for item in utterances
    ]


def format_timestamp(seconds: float) -> str:
    seconds = max(
        float(seconds or 0),
        0.0,
    )
    minutes, remaining = divmod(
        seconds,
        60,
    )
    hours, minutes = divmod(
        int(minutes),
        60,
    )
    return (
        f"{hours:02d}:"
        f"{minutes:02d}:"
        f"{remaining:06.3f}"
    )


def render_speaker_utterances(
    utterances: list[SpeakerUtterance],
) -> str:
    return "\n\n".join(
        (
            f"[{format_timestamp(item.start)}–"
            f"{format_timestamp(item.end)}] "
            f"{item.speaker}:\n"
            f"{item.text}"
        )
        for item in utterances
        if item.text
    ).strip()


def transform_utterances(
    utterances: list[SpeakerUtterance],
    text_transform,
) -> list[SpeakerUtterance]:
    transformed: list[
        SpeakerUtterance
    ] = []

    for item in utterances:
        transformed.append(
            SpeakerUtterance(
                speaker=item.speaker,
                start=item.start,
                end=item.end,
                text=text_transform(
                    item.text
                ),
                word_count=item.word_count,
                average_score=(
                    item.average_score
                ),
            )
        )

    return transformed
