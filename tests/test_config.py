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
    from_timestamp_float = 1651369964.0
    from_timestamp_date = datetime(2022, 5, 1, 1, 52, 44, tzinfo=pytz.utc)
    to_timestamp_int = int(datetime.now().timestamp())
    to_timestamp_float = float(datetime.now().timestamp())
    to_timestamp_date = datetime.now()
    resp = bayes_emh.get_games_list(from_timestamp=from_timestamp_int, limit=10)
    assert isinstance(resp, list)
    resp = bayes_emh.get_games_list(from_timestamp=from_timestamp_float, limit=10)
    assert isinstance(resp, list)
    resp = bayes_emh.get_games_list(from_timestamp=from_timestamp_date, limit=1000)
    assert isinstance(resp, list)
    resp = bayes_emh.get_games_list(from_timestamp=from_timestamp_int, to_timestamp=to_timestamp_date, limit=10)
    assert isinstance(resp, list)
    resp = bayes_emh.get_games_list(from_timestamp=from_timestamp_date, to_timestamp=to_timestamp_float, limit=10)
    assert isinstance(resp, list)
    resp = bayes_emh.get_games_list(from_timestamp=from_timestamp_float, to_timestamp=to_timestamp_int, limit=10)
    assert isinstance(resp, list)
    resp = bayes_emh.get_games_list(from_timestamp=from_timestamp_float, to_timestamp=to_timestamp_int, tags=tags,
                                    limit=10)
    assert isinstance(resp, list)
    resp = bayes_emh.get_games_list(tags=tags, limit=10)
    assert isinstance(resp, list)
    resp = bayes_emh.get_games_list(tags=tags, team1="ISG")
    assert isinstance(resp, list)
    resp = bayes_emh.get_games_list(tags=tags, team1="ISG", team2="EST")
    assert isinstance(resp, list)
    resp = bayes_emh.get_games_list(limit=600)
    assert isinstance(resp, list)
    assert len(resp) == 600
    seen_platform_game_ids = []
    for game in resp:
        assert game["platformGameId"] not in seen_platform_game_ids
        seen_platform_game_ids.append(game["platformGameId"])
    resp = bayes_emh.get_games_list(max_page_size=40, limit=20)
    assert len(resp) == 20
    assert isinstance(resp, list)
    resp = bayes_emh.get_games_list(max_page_size=40, limit=70)
    assert len(resp) == 70
    assert isinstance(resp, list)
    resp = bayes_emh.get_games_list(tags=tags, team1="ISG", team2="EST", limit=20)
    assert isinstance(resp, list)
    resp = bayes_emh.get_games_list(max_page_size=2000)
    assert isinstance(resp, list)
