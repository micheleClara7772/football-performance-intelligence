"""Métriques avancées sans tracking ni vidéos de fournisseur dans le repo."""
from fpi.analysis.advanced import advanced_metrics_by_period, ADVANCED_LABELS
from fpi.ai.free_text import free_text_answer

TEAMS=("Morocco","Portugal")


def ev(typ,minute,second=0,team="Morocco",period=1,**extra):
    return {
        "id": f"{typ}-{minute}-{second}-{period}",
        "type":{"name":typ},"team":{"name":team},"period":period,
        "minute":minute,"second":second,**extra,
    }


def test_advanced_metrics_documented_proxy_definitions():
    events=[
        ev("Pressure",12,2),
        ev("Pass",12,3,location=[40,10], **{"pass":{"end_location":[70,55],"shot_assist":True}}),
        ev("Ball Recovery",12,5,location=[87,40]),
        ev("Shot",13,1,location=[108,40],shot={"statsbomb_xg":0.2}),
        ev("Pass",14,0,location=[70,30], **{"pass":{"end_location":[95,30],"outcome":{"name":"Incomplete"}}}),
        ev("Pass",15,0,location=[50,10], **{"pass":{"end_location":[70,50],"goal_assist":True}}),
        ev("Ball Recovery",16,1,location=[55,40]),
        ev("Ball Recovery",17,1,location=[60,40]),
        ev("Pressure",20,2,period=3),
        ev("Ball Recovery",20,4,period=3,location=[100,40]),
    ]
    data=advanced_metrics_by_period(events,TEAMS)
    r=data[(data.team=="Morocco")&(data.period==1)].iloc[0]
    assert r.progressive_passes==2
    assert r.switches_of_play==2
    assert r.high_recoveries==2
    assert r.final_third_recoveries==1
    assert r.shot_assists==1
    assert r.goal_assists==1
    assert r.box_shots==1
    assert r.pressures_then_recovery_8s==1
    assert len(data)==4 and data.drop(columns=["team","period"]).select_dtypes("number").fillna(0).ge(0).all().all()
    assert len(ADVANCED_LABELS)==8


def test_invalid_coordinates_and_unsourced_possession_ignored():
    events=[
        ev("Pass",1,1,location=[True,10],**{"pass":{"end_location":[70,60]}}),
        ev("Pass",2,1,location=[50,40],**{"pass":{"end_location":[130,40]}}),
        ev("Shot",3,1,location=[130,40],shot={}),
        ev("Ball Recovery",4,1,location=[130,40]),
    ]
    r=advanced_metrics_by_period(events,TEAMS).iloc[0]
    assert r.progressive_passes==0
    assert r.box_shots==0
    assert r.high_recoveries==0
    import pandas as pd
    assert pd.isna(r.possessions_annotated)  # unknown, not zero


def test_free_text_advanced_signals_for_match(events):
    message=free_text_answer(events,TEAMS,"Morocco","Combien de passes progressives pour le Maroc ?")
    assert "passes progressives" in message and "StatsBomb" in message
