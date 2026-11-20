import test from 'node:test';
import assert from 'node:assert/strict';
import {serve,modes,scenarios} from '../lib/service.js';
import {createHash} from 'node:crypto';
test('Recherche par zone, période et événements vérifiables',()=>{
 const state={users:[],sessions:[],dossiers:[]};
 const bootstrap=createHash('sha256').update('start').digest('hex');
 const key=serve(state,{action:'activate',code:'start',password:'0123456789abcdefgh'},null,bootstrap).cookie;
 const run=(action,params)=>serve(state,{action,...params},key,bootstrap).body;
 const {id}=run('create',{mode:modes[0],scenario:scenarios[0],team:'Maroc'});
 const {items}=run('detail',{id});
 for(const [q,criteria] of [
   ['Compare les entrées dans le dernier tiers entre les deux mi-temps',e=>e.tags.includes('Entrée dans le dernier tiers')],
   ['Progressions par le côté droit',e=>e.y>=160/3&&e.tags.some(t=>t.endsWith('progressive'))],
   ['Conduites progressives en première mi-temps',e=>e.p===1&&e.tags.includes('Conduite progressive')],
 ]){
    assert.deepEqual(run('ask',{id,q}).ids,items.filter(criteria).map(e=>e.id));
 }
 for(const q of ['Pourquoi ce pressing ?', 'droite et gauche', 'quelle est sa vitesse ?', 'Combien de passes de Ronaldo ?']){
    assert.deepEqual(run('ask',{id,q}).ids,[]);
 }
});
