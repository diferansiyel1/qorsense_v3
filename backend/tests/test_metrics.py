"""
Metrics Calculation Tests

Tests for sensor analysis metrics calculation functions.
"""

import pytest
import numpy as np
from backend.analysis import SensorAnalyzer


@pytest.fixture
def analyzer():
    """Create a SensorAnalyzer instance."""
    return SensorAnalyzer()


@pytest.fixture
def clean_signal():
    """Generate a clean sinusoidal signal."""
    t = np.linspace(0, 10, 100)
    return np.sin(t) * 10 + np.random.normal(0, 0.1, 100)


@pytest.fixture
def noisy_signal():
    """Generate a noisy signal."""
    t = np.linspace(0, 10, 100)
    return np.sin(t) * 10 + np.random.normal(0, 3.0, 100)


@pytest.fixture
def drifting_signal():
    """Generate a signal with drift."""
    t = np.linspace(0, 10, 100)
    drift = np.linspace(0, 5, 100)
    return np.sin(t) * 10 + drift + np.random.normal(0, 0.1, 100)


def test_preprocessing(analyzer, clean_signal):
    """Test data preprocessing."""
    # Add some NaN values
    signal_with_nan = clean_signal.copy()
    signal_with_nan[10] = np.nan
    signal_with_nan[20] = np.nan
    
    processed = analyzer.preprocessing(signal_with_nan.tolist())
    
    # Should remove NaN values
    assert len(processed) < len(signal_with_nan)
    assert not np.any(np.isnan(processed))


def test_calc_bias(analyzer, clean_signal):
    """Test bias calculation."""
    bias = analyzer.calc_bias(clean_signal)
    
    # Bias should be close to 0 for centered sinusoid
    assert isinstance(bias, (int, float))
    assert abs(bias) < 1.0  # Should be small


def test_calc_slope(analyzer, drifting_signal):
    """Test slope calculation."""
    slope = analyzer.calc_slope(drifting_signal)
    
    # Should detect positive drift
    assert isinstance(slope, (int, float))
    assert slope > 0  # Drifting signal has positive slope


def test_calc_snr_db(analyzer, clean_signal, noisy_signal):
    """Test SNR calculation."""
    snr_clean = analyzer.calc_snr_db(clean_signal)
    snr_noisy = analyzer.calc_snr_db(noisy_signal)
    
    # Clean signal should have higher SNR
    assert isinstance(snr_clean, (int, float))
    assert isinstance(snr_noisy, (int, float))
    assert snr_clean > snr_noisy


def test_calc_hysteresis(analyzer, clean_signal):
    """Test hysteresis calculation."""
    hysteresis, hyst_x, hyst_y = analyzer.calc_hysteresis(clean_signal)
    
    assert isinstance(hysteresis, (int, float))
    assert isinstance(hyst_x, list)
    assert isinstance(hyst_y, list)
    assert len(hyst_x) == len(hyst_y)


def test_calc_dfa(analyzer, clean_signal):
    """Test DFA (Detrended Fluctuation Analysis) calculation."""
    hurst, r2, scales, fluctuations = analyzer.calc_dfa(clean_signal)
    
    assert isinstance(hurst, (int, float))
    assert isinstance(r2, (int, float))
    assert isinstance(scales, list)
    assert isinstance(fluctuations, list)
    assert 0 <= hurst <= 1  # Hurst exponent should be in [0, 1]
    assert 0 <= r2 <= 1  # R² should be in [0, 1]


def test_get_health_score_healthy(analyzer, clean_signal):
    """Test health score for healthy signal."""
    # Prepare metrics
    clean_data = analyzer.preprocessing(clean_signal.tolist())
    bias = analyzer.calc_bias(clean_data)
    slope = analyzer.calc_slope(clean_data)
    noise_std = float(np.std(clean_data))
    snr_db = analyzer.calc_snr_db(clean_data)
    hysteresis, hyst_x, hyst_y = analyzer.calc_hysteresis(clean_data)
    hurst, hurst_r2, dfa_scales, dfa_flucts = analyzer.calc_dfa(clean_data)
    
    metrics = {
        "bias": bias,
        "slope": slope,
        "noise_std": noise_std,
        "snr_db": snr_db,
        "hysteresis": hysteresis,
        "hurst": hurst
    }
    
    health = analyzer.get_health_score(metrics)
    
    assert isinstance(health, dict)
    assert "score" in health
    assert "status" in health
    assert "diagnosis" in health
    assert "flags" in health
    assert "recommendation" in health
    assert 0 <= health["score"] <= 100


def test_analyze_end_to_end(analyzer, clean_signal):
    """Test complete analysis pipeline."""
    result = analyzer.analyze(clean_signal.tolist())
    
    assert isinstance(result, dict)
    assert "metrics" in result
    assert "health" in result
    assert "prediction" in result
    
    # Check health structure
    health = result["health"]
    assert "score" in health
    assert "status" in health
    assert "diagnosis" in health
    assert "flags" in health
    assert "recommendation" in health
