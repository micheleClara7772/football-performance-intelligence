"""Full-period coverage contracts, without external media."""
from types import SimpleNamespace
from scripts.analyze_soccertrack_full_half import temporal_coverage


def summary(times, duration):
    return SimpleNamespace(
        per_frame=[{"time_seconds":t} for t in times],
        duration_seconds=duration,
        sampled_frames=len(times),
    )


def test_cover_45min_without_claiming_every_frame():
    report=temporal_coverage(summary(list(range(0,2700,15)),2700.0),
                             interval_seconds=15)
    assert report["decoded_sample_count"]==180
    assert report["coverage_95pct_of_requested_timestamps"]
    assert report["last_decoded_sample_seconds"]==2685
    assert report["all_source_frames_analyzed"] is False
    assert report["continuous_tracking"] is False


def test_missing_second_half_segment_cannot_appear_fully_covered():
    report=temporal_coverage(summary(list(range(0,2100,15)),2700.0),
                             interval_seconds=15)
    assert report["coverage_95pct_of_requested_timestamps"] is False


def test_disconnected_timestamps_near_end_but_few_samples_fail():
    report=temporal_coverage(summary([0,1000,2000,2685],2700.0),
                             interval_seconds=15)
    assert report["coverage_95pct_of_requested_timestamps"] is False
