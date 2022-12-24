import bayes_lol_client
from datetime import datetime
import pytz

sample_ids = ["ESPORTSTMNT01_3268705", "ESPORTSTMNT03_2052838"]
sample_replay_ids = ["ESPORTSTMNT01_3268705", "ESPORTSTMNT02_3130581"]

bayes_emh = bayes_lol_client.BayesEMH()


def test_get_game_summary():
    for sample_id in sample_ids:
        resp = bayes_emh.get_game_summary(sample_id)
        assert isinstance(resp, dict)


def test_get_game_details():
    for sample_id in sample_ids:
        resp = bayes_emh.get_game_details(sample_id)
        assert isinstance(resp, dict)


def test_get_game_replay():
    for sample_id in sample_replay_ids:
        resp = bayes_emh.get_game_replay(sample_id)
        assert isinstance(resp, bytes)


def test_get_game_data():
    for sample_id in sample_ids:
        resp = bayes_emh.get_game_data(sample_id)
        assert isinstance(resp, tuple)


def test_get_tags_list():
    resp = bayes_emh.get_tags_list()
    assert isinstance(resp, list)


def test_get_games_info():
    resp = bayes_emh.get_games_info(sample_ids)
    assert isinstance(resp, dict)


def test_get_game_info():
    for sample_id in sample_ids:
        resp = bayes_emh.get_game_info(sample_id)
        assert isinstance(resp, dict)


def test_get_game_list():
    tags = ["LLA", "LEC"]
    from_timestamp_int = 1651369964
    from_timestamp_float = float(1651369964.0)
    from_timestamp_date = datetime(2022, 5, 1, 1, 52, 44, tzinfo=pytz.timezone("America/Argentina/Buenos_Aires"))
    to_timestamp_int = int(datetime.now().timestamp())
    to_timestamp_float = float(datetime.now().timestamp())
    to_timestamp_date = datetime.now()
    resp = bayes_emh.get_game_list(from_timestamp=from_timestamp_int)
    assert isinstance(resp, dict)
    resp = bayes_emh.get_game_list(from_timestamp=from_timestamp_float)
    assert isinstance(resp, dict)
    resp = bayes_emh.get_game_list(from_timestamp=from_timestamp_date)
    assert isinstance(resp, dict)
    resp = bayes_emh.get_game_list(from_timestamp=from_timestamp_int, to_timestamp=to_timestamp_date)
    assert isinstance(resp, dict)
    resp = bayes_emh.get_game_list(from_timestamp=from_timestamp_date, to_timestamp=to_timestamp_float)
    assert isinstance(resp, dict)
    resp = bayes_emh.get_game_list(from_timestamp=from_timestamp_float, to_timestamp=to_timestamp_int)
    assert isinstance(resp, dict)
    resp = bayes_emh.get_game_list(from_timestamp=from_timestamp_float, to_timestamp=to_timestamp_int, tags=tags)
    assert isinstance(resp, dict)
    resp = bayes_emh.get_game_list(tags=tags)
    assert isinstance(resp, dict)
    resp = bayes_emh.get_game_list(tags=tags, team1="ISG")
    assert isinstance(resp, dict)
