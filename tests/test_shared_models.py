# tests/test_shared_models.py
# Test modèles partagés unifiés

import pytest
from datetime import datetime
from phoenix_shared_models import Letter, CV, UserProfile, Skill, Experience

def test_letter_model_basic():
    """Test modèle Letter partagé de base"""
    
    letter = Letter(
        letter_id="test_123",
        job_title="Développeur Python",
        company="Phoenix Corp", 
        content_hash="abc123",
        content="Contenu de la lettre...",
        user_id="user_456",
        created_at=datetime.now(),
        quality_score=85.5,
        tone_type="formal",
        is_career_change=False
    )
    
    assert letter.letter_id == "test_123"
    assert letter.job_title == "Développeur Python"
    assert letter.quality_score == 85.5
    assert letter.tone_type == "formal"
    assert not letter.is_career_change
    print("✅ Letter model OK")

def test_cv_model_basic():
    """Test modèle CV partagé"""
    
    cv = CV(
        cv_id="cv_789",
        content_hash="def456",
        ats_score=92.0,
        keywords=["Python", "Django", "PostgreSQL"]
    )
    
    assert cv.cv_id == "cv_789"
    assert cv.ats_score == 92.0
    assert len(cv.keywords) == 3
    assert "Python" in cv.keywords
    print("✅ CV model OK")

def test_user_profile_complete():
    """Test UserProfile avec tous les composants"""
    
    # Compétences
    skills = [
        Skill(name="Python", level=4),
        Skill(name="PostgreSQL", level=3)
    ]
    
    # Expériences
    from datetime import date
    experiences = [
        Experience(
            title="Développeur Senior",
            company="TechCorp",
            start_date=date(2022, 1, 1),
            end_date=date(2024, 1, 1),
            description="Développement applications web"
        )
    ]
    
    # CV générés
    generated_cvs = [
        CV(cv_id="cv_1", content_hash="hash1", ats_score=88.0, keywords=["Python"])
    ]
    
    # Lettres générées
    generated_letters = [
        Letter(
            letter_id="letter_1",
            job_title="Dev",
            company="Test",
            content_hash="hash2",
            content="Test content",
            user_id="user_123"
        )
    ]
    
    # Profil complet
    profile = UserProfile(
        user_id="user_123",
        email="test@phoenix.com",
        first_name="John",
        last_name="Doe",
        skills=skills,
        experiences=experiences,
        generated_cvs=generated_cvs,
        generated_letters=generated_letters,
        mood_history=[{"date": "2024-01-01", "mood": 0.8}],
        coaching_sessions=5
    )
    
    assert profile.user_id == "user_123"
    assert profile.email == "test@phoenix.com"
    assert len(profile.skills) == 2
    assert len(profile.experiences) == 1
    assert len(profile.generated_cvs) == 1
    assert len(profile.generated_letters) == 1
    assert profile.coaching_sessions == 5
    
    print("✅ UserProfile complet OK")

def test_models_data_consistency():
    """Test cohérence des données entre modèles"""
    
    user_id = "consistent_user_456"
    
    # Letter avec user_id
    letter = Letter(
        letter_id="letter_consistency",
        job_title="Test Job",
        company="Test Company",
        content_hash="hash_test",
        content="Test content",
        user_id=user_id
    )
    
    # Profile avec même user_id
    profile = UserProfile(
        user_id=user_id,
        email="consistent@test.com",
        first_name="Test",
        last_name="User",
        generated_letters=[letter]
    )
    
    # Vérifier cohérence
    assert profile.user_id == letter.user_id
    assert profile.generated_letters[0].letter_id == letter.letter_id
    
    print("✅ Cohérence modèles OK")

def test_models_edge_cases():
    """Test cas limites des modèles"""
    
    # Letter minimale
    letter_min = Letter(
        letter_id="min",
        job_title="Job",
        company="Company", 
        content_hash="hash",
        content="Content",
        user_id="user"
    )
    
    assert letter_min.created_at is None  # Optionnel
    assert letter_min.quality_score is None  # Optionnel
    assert letter_min.tone_type is None  # Optionnel
    assert not letter_min.is_career_change  # Default False
    
    # Profile minimal
    profile_min = UserProfile(
        user_id="min_user",
        email="min@test.com",
        first_name=None,
        last_name=None
    )
    
    assert len(profile_min.skills) == 0  # Liste vide par défaut
    assert len(profile_min.experiences) == 0
    assert len(profile_min.generated_cvs) == 0
    assert len(profile_min.generated_letters) == 0
    assert profile_min.coaching_sessions == 0
    
    print("✅ Cas limites modèles OK")