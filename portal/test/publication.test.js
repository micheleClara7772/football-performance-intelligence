import test from 'node:test';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {serve,modes,scenarios} from '../lib/service.js';
test('Accès, deux scénarios, publication, version précédente et rejet',()=>{
 const state={users:[],sessions:[],dossiers:[]};
 const call=(key,action,fields={})=>serve(state,{action,...fields},key,createHash('sha256').update('bootstrap').digest('hex'));
 const admin=call(null,'activate',{code:'bootstrap',password:'exemple-long-pour-test'}).cookie;
 function account(name,role){const {code}=call(admin,'invite',{name,role}).body;return call(null,'activate',{code,password:'exemple-long-pour-test'}).cookie}
 const staff=account('Analyste','Staff'),coach=account('Coach','Entraîneur'),other=account('Autre','Staff');
 for(const team of ['Maroc','Portugal'])for(const scenario of scenarios)for(const mode of modes){
   const {id}=call(staff,'create',{scenario,mode,team}).body;
   const detail=()=>call(staff,'detail',{id}).body;
   const update=(a,extra={})=>call(staff,a,{id,version:detail().version,...extra});
   const items=detail().items;assert.ok(items.length>0);assert.ok(items.every(e=>e.team===team&&e.p<=2));
   for(const action of ['detail','ask'])assert.throws(()=>call(coach,action,{id,q:'passe'}));
   assert.throws(()=>call(other,'detail',{id}));assert.throws(()=>call(coach,'publish',{id}));
   update('review');assert.throws(()=>update('validate'));update('mark',{event:items[0].id,decision:'Retenue',note:'Première lecture'});
   update('validate');update('publish');update('review');
   update('mark',{event:items[0].id,decision:'Retenue',note:'Privé'});
   assert.equal(call(coach,'detail',{id}).body.items[0].note,'Première lecture');assert.equal(call(coach,'detail',{id}).body.items.length,1);
   assert.deepEqual(call(coach,'ask',{id,q:'Compare les mi-temps'}).body.ids,[items[0].id]);
   assert.deepEqual(call(coach,'ask',{id,q:'quelle vitesse ?'}).body.ids,[]);
   assert.throws(()=>call(staff,'reject',{id,version:1}));update('reject');
   assert.equal(call(coach,'detail',{id}).body.items[0].note,'Première lecture');
 }
});
