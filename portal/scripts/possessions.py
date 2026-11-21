from itertools import groupby

KINDS = {'Pass':'Passe','Carry':'Conduite','Shot':'Tir','Miscontrol':'Contrôle manqué','Dispossessed':'Dépossession','Dribble':'Dribble'}
RESULT = {'Incomplete':'incomplète','Out':'sortie','Offside':'hors-jeu','Goal':'but','Saved':'arrêté','Off T':'non cadré','Blocked':'contré','Post':'poteau','Wayward':'non cadré','Complete':'réussi','Unknown':'issue inconnue'}


def enrich(events, rows, teams):
    times = lambda e: e['minute']*60+e['second']
    phases, goals = {}, []
    score = [0, 0]
    by_id = {r['id']:r for r in rows}
    groups = [(key,list(group)) for key,group in groupby(events,key=lambda e:(e['period'],e['possession']))]
    for i, ((period, number), group) in enumerate(groups):
        if period > 4:
            continue
        key = str(number)
        owner = group[0]['possession_team']['name']
        steps = []
        for e in group:
            kind = e['type']['name']
            team = e['team']['name']
            data = e.get(kind.lower(), {})
            outcome = data.get('outcome', {}).get('name')
            if e['id'] in by_id:
                by_id[e['id']].update(phase=key, score=list(score),recipient=data.get('recipient',{}).get('name'))
            if (kind == 'Shot' and outcome == 'Goal') or kind == 'Own Goal For':
                score[teams.index(team)] += 1
                goals.append(dict(p=period,t=times(e),team=team,score=list(score),phase=key))
            if team == owner and kind in KINDS and e.get('location'):
                steps.append(dict(id=e['id'], t=times(e), kind=KINDS[kind],player=e.get('player',{}).get('name','Collectif'),recipient=data.get('recipient',{}).get('name'),xy=e['location'][:2],end=data.get('end_location',[])[:2],result=RESULT.get(outcome,outcome or '')))
        next_owner = groups[i+1][1][0]['possession_team']['name'] if i+1<len(groups) and groups[i+1][0][0]==period else None
        outcome = 'Fin de période' if not next_owner else ('Possession suivante adverse' if next_owner!=owner else 'Nouvelle possession de la même équipe')
        phases[key]=dict(id=key,p=period,start=times(group[0]),finish=times(group[-1]),steps=steps,outcome=outcome)
    return phases,goals
