import test from 'node:test';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {serve,modes,scenarios} from '../lib/service.js';
test('Horloges, suivi joueur, instantanés et sources vidéo sur deux matchs',()=>{
 const state={users:[],sessions:[],dossiers:[]};
 const hash=createHash('sha256').update('set').digest('hex');
 const account=(code)=>serve(state,{action:'activate',code,password:'secret-test-fixture'},null,hash).cookie;
 const admin=account('set');
 const run=(action,fields={},key=admin)=>serve(state,{action,...fields},key,hash).body;
 const coach=account(run('invite',{name:'coach',role:'Entraîneur'}).code);
 const {matches}=run('home');
 assert.equal(matches.length,2);
 for(const m of matches)for(const team of m.teams)for(const scenario of scenarios){
   const {id}=run('create',{matchId:m.id,mode:modes[0],team,scenario});
   const detail=run('detail',{id});
   assert.ok(detail.items.length>0);
   assert.equal(detail.range.to,Object.values(m.ends).at(-1));
   for(const e of detail.items){
    assert.equal(e.team,team);assert.ok(e.start<=e.finish&&e.finish<=m.ends[e.p]);
   }
 }
 const range={fromPeriod:1,from:300,toPeriod:1,to:360};
 const params={matchId:'3869486',mode:modes[1],team:'Maroc',scenario:scenarios[0],range};
 assert.throws(()=>run('create',{...params,range:{...range,to:1}}));
 const {id}=run('create',params);
 function update(action,fields={}){return run(action,{id,version:run('detail',{id}).version,...fields})}
 const detail=run('detail',{id});assert.deepEqual(detail.range,range);
 const e=detail.items.find(e=>e.clock==='05:12');assert.ok(e.player.includes('Amallah'));
 update('review');
 update('metadata',{title:'Franchir le dernier tiers',summary:'Lecture retenue',discussion:'Comment répéter la sortie ?',includeTotal:true});
 update('mark',{event:e.id,decision:'Retenue',note:'Une passe vers le dernier tiers.',clip:{url:'https://example.org/test-fixture.mp4',checked:true,start:10}});
 update('validate');update('publish');update('review');
 update('metadata',{title:'Titre confidentiel',summary:'Brouillon',discussion:'',includeTotal:false});
 const pub=run('detail',{id},coach);
 assert.equal(pub.title,'Franchir le dernier tiers');assert.equal(pub.total,detail.items.length);assert.equal(pub.items[0].clip.start,10);
 assert.equal(run('home',{},coach).dossiers.find(d=>d.id===id).title,pub.title);
 const found=run('ask',{id,q:'Est-ce qu’Amallah a trouvé plusieurs fois cette passe ?',context:{event:e.id}},coach);
 assert.deepEqual(found.ids,[e.id]);
 assert.deepEqual(run('ask',{id,q:'Montre-moi ses autres passes',context:found.context},coach).ids,[]);
 assert.throws(()=>update('delete'));update('archive');assert.throws(()=>run('detail',{id},coach));
});
