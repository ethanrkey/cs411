import pytest
from meal_max.models.battle_model import BattleModel
from meal_max.models.kitchen_model import Meal, update_meal_stats
from unittest.mock import patch


@pytest.fixture()
def battle_model():
    """Fixture to provide a new instance of BattleModel for each test."""
    return BattleModel()


@pytest.fixture
def sample_meal1():
    return Meal(id=1, meal='Sushi', cuisine='Japanese', price=20.0, difficulty='MED')


@pytest.fixture
def sample_meal2():
    return Meal(id=2, meal='Pasta', cuisine='Italian', price=15.0, difficulty='LOW')


##################################################
# Combatant Management Test Cases
##################################################

def test_prep_combatant(battle_model, sample_meal1):
    """Test adding a combatant to the battle."""
    battle_model.prep_combatant(sample_meal1)
    assert len(battle_model.combatants) == 1
    assert battle_model.combatants[0].meal == 'Sushi'


def test_prep_combatant_full(battle_model, sample_meal1, sample_meal2):
    """Test error when adding more than two combatants."""
    battle_model.prep_combatant(sample_meal1)
    battle_model.prep_combatant(sample_meal2)
    with pytest.raises(ValueError, match="Combatant list is full, cannot add more combatants."):
        battle_model.prep_combatant(sample_meal1)


def test_clear_combatants(battle_model, sample_meal1, sample_meal2):
    """Test clearing the combatants list."""
    battle_model.prep_combatant(sample_meal1)
    battle_model.prep_combatant(sample_meal2)
    battle_model.clear_combatants()
    assert len(battle_model.combatants) == 0, "Combatants list should be empty after clearing"


##################################################
# Battle Test Cases
##################################################

@patch("meal_max.models.battle_model.get_random", return_value=0.1)
@patch("meal_max.models.kitchen_model.update_meal_stats")
def test_battle_determines_winner(mock_update_meal_stats, mock_get_random, battle_model, sample_meal1, sample_meal2):
    """Test determining a winner between two combatants."""
    battle_model.prep_combatant(sample_meal1)
    battle_model.prep_combatant(sample_meal2)


    winner = battle_model.battle()
    assert winner in [sample_meal1.meal, sample_meal2.meal]
    assert len(battle_model.combatants) == 1, "Expected one combatant remaining after battle"
    mock_update_meal_stats.assert_any_call(sample_meal1.id, 'win')
    mock_update_meal_stats.assert_any_call(sample_meal2.id, 'loss')


def test_battle_not_enough_combatants(battle_model, sample_meal1):
    """Test error when trying to start a battle with fewer than two combatants."""
    battle_model.prep_combatant(sample_meal1)
    with pytest.raises(ValueError, match="Two combatants must be prepped for a battle."):
        battle_model.battle()


##################################################
# Score Calculation Test Cases
##################################################

def test_get_battle_score_medium_difficulty(battle_model, sample_meal1):
    """Test battle score calculation for a meal with medium difficulty."""
    score = battle_model.get_battle_score(sample_meal1)
    expected_score = (sample_meal1.price * len(sample_meal1.cuisine)) - 2  # MED has modifier of 2
    assert score == expected_score, f"Expected score to be {expected_score}, but got {score}"


def test_get_battle_score_low_difficulty(battle_model, sample_meal2):
    """Test battle score calculation for a meal with low difficulty."""
    score = battle_model.get_battle_score(sample_meal2)
    expected_score = (sample_meal2.price * len(sample_meal2.cuisine)) - 3  # LOW has modifier of 3
    assert score == expected_score, f"Expected score to be {expected_score}, but got {score}"


def test_get_battle_score_high_difficulty(battle_model):
    """Test battle score calculation for a meal with high difficulty."""
    high_difficulty_meal = Meal(id=3, meal='Steak', cuisine='American', price=25.0, difficulty='HIGH')
    score = battle_model.get_battle_score(high_difficulty_meal)
    expected_score = (high_difficulty_meal.price * len(high_difficulty_meal.cuisine)) - 1  # HIGH has modifier of 1
    assert score == expected_score, f"Expected score to be {expected_score}, but got {score}"


##################################################
# Combatant Retrieval Test Case
##################################################

def test_get_combatants(battle_model, sample_meal1, sample_meal2):
    """Test retrieving the list of combatants."""
    battle_model.prep_combatant(sample_meal1)
    battle_model.prep_combatant(sample_meal2)
    combatants = battle_model.get_combatants()
    assert len(combatants) == 2, "Expected two combatants in the list"
    assert combatants[0].meal == sample_meal1.meal
    assert combatants[1].meal == sample_meal2.meal