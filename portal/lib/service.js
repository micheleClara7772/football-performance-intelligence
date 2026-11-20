import { randomBytes, randomUUID, createHash, scryptSync, timingSafeEqual } from 'node:crypto';
import { readFileSync } from 'node:fs';
import { gunzipSync } from 'node:zlib';
import { join } from 'node:path';
const rows = JSON.parse(gunzipSync(readFileSync(join(process.cwd(),'lib/evidence.json.gz'))));
export const modes=['Préparer un adversaire','Débriefer mon équipe'];
export const scenarios=['Progression offensive','Transitions après perte'];
const roles=['Administrateur','Staff','Entraîneur'];
const now=()=>new Date().toISOString();
const hash=s=>createHash('sha256').update(s).digest('hex');
const token=()=>randomBytes(32).toString('base64url');
const requireThat=(ok,msg='Accès refusé.',status=403)=>{if(!ok)throw Object.assign(Error(msg),{status})};
const normalize=s=>s.normalize('NFD').replace(/\p{M}/gu,'').toLowerCase();
const safe=(s,max=512)=>typeof s==='string'&&s.length>0&&s.length<=max;
function password(value,salt=randomBytes(16).toString('hex')){
  return salt+':'+scryptSync(value,salt,32).toString('hex');
}
function invitation(state,name,role){
  requireThat(safe(name,64)&&roles.includes(role)&&!state.users.some(u=>u.name===name),'Nom indisponible ou rôle invalide.',400);
  const code=token();
  state.users.push({id:randomUUID(),name,role,invite:hash(code),until:Date.now()+86400000});
  return code;
}
function openSession(state,user){
  const raw=token();
  state.sessions=state.sessions.filter(s=>s.expires>Date.now());
  state.sessions.push({user:user.id,key:hash(raw),expires:Date.now()+8*3600000});
  return {cookie:raw,body:{success:true},write:true};
}
function answer(input,items){
  const q=normalize(input);
  const words=q.match(/[a-z0-9]+/g)||[];
  const known=/^(retrouve|rechercher?|cherche|trouve|montre|affiche|compare[rz]?|combien|quels?|quelles?|quelle|ou|y|a|t|il|les?|la|l|d|du|de|des|un|une|en|au|aux|dans|dans|par|sur|ce|cette|ces|celles|sont|ont|est|ete|entre|et|aussi|apres|avec|pour|moi|nous|toutes?|tous|deux|1|2|1re|2e|premiere|seconde|deuxieme|mi|temps|periodes?|entrees?|dernier|tiers|renversements?|changements?|cotes?|droite?s?|gauche?s?|axe|pertes?|balle|ballon|transitions?|passes?|conduites?|progressions?|progressives?|offensives?|actions?|situations?|observations?|correspondent|match|dossier|selection|nombre|total)$/;
  const clarification={message:'Précisez une action (perte, passe, conduite, renversement, entrée), une zone ou une mi-temps dans ce dossier.',ids:[]};
  if(words.some(word=>!known.test(word)))return clarification;
  const tags=[[/entree/,'Entrée dans le dernier tiers'],[/renversement|changement de cote/,'Renversement'],[/perte|transition/,'Perte candidate'],[/passe/,'Passe progressive'],[/conduite/,'Conduite progressive']];
  const keys=tags.filter(([re])=>re.test(q)).map(t=>t[1]);
  const compare=/compar|mi.temps|periode/.test(q);
  const right=/droit/.test(q), left=/gauche/.test(q);
  if((right&&left)||(!keys.length&&!compare&&!right&&!left&&!/axe/.test(q)&&!/progression|action|situation|observation/.test(q))||/pourquoi|pressing|xg|score|brouillon|vitesse|butteur|buteur|distance|bless|possession|hors.jeu/.test(q)) return {message:'Cette question dépasse les preuves disponibles. Précisez une action, un côté ou une mi-temps.',ids:[]};
  let selected=items.filter(e=>(!keys.length||keys.some(k=>e.tags.includes(k)))&&(!right||e.y>=160/3)&&(!left||e.y<80/3));
  if(/progression/.test(q)&&!keys.length)selected=selected.filter(e=>e.tags.some(t=>t.endsWith('progressive')));
  if(/axe/.test(q))selected=selected.filter(e=>e.y>=80/3&&e.y<160/3);
  if(/dernier tiers/.test(q)&&!keys.includes('Entrée dans le dernier tiers'))selected=selected.filter(e=>e.x>=80);
  if(/premiere|1re/.test(q)&&!/compar/.test(q))selected=selected.filter(e=>e.p===1);
  if(/seconde|deuxieme|2e/.test(q)&&!/compar/.test(q))selected=selected.filter(e=>e.p===2);
  return {message:selected.length+' action(s) dans la sélection. Première mi-temps : '+selected.filter(e=>e.p===1).length+' · Seconde : '+selected.filter(e=>e.p===2).length+'.',ids:selected.map(e=>e.id)};
}
export function serve(state,body,sessionKey,bootstrapHash){
  const {action}=body;
  const result=(data,write=false)=>({body:data,write});
  if(action==='activate'){
    requireThat(safe(body.code)&&safe(body.password,128)&&body.password.length>=12,'Code ou mot de passe invalide.',400);
    const digest=hash(body.code);
    let user=state.users.find(u=>u.invite===digest&&u.until>Date.now()&&!u.disabled);
    if(!user&&!state.users.length&&bootstrapHash&&digest===bootstrapHash){
      user={id:randomUUID(),name:'Clara',role:'Administrateur'};state.users.push(user);
    }
    requireThat(user,'Invitation invalide ou expirée.',401);
    user.password=password(body.password);delete user.invite;delete user.until;
    return openSession(state,user);
  }
  if(action==='login'){
    const user=state.users.find(u=>u.name===body.name&&!u.disabled);
    requireThat(safe(body.password,128),'Connexion refusée.',401);
    const stored=user?.password||'00000000000000000000000000000000:'+ '0'.repeat(64);
    const candidate=password(body.password,stored.split(':')[0]);
    requireThat(timingSafeEqual(Buffer.from(candidate),Buffer.from(stored))&&user?.password,'Connexion refusée.',401);
    return openSession(state,user);
  }
  const session=state.sessions.find(s=>s.key===hash(sessionKey||'')&&s.expires>Date.now());
  const user=state.users.find(u=>u.id===session?.user&&!u.disabled);requireThat(user,'Connectez-vous.',401);
  const admin=user.role===roles[0], staff=user.role!==roles[2];
  const mine=d=>admin||d.owner===user.id;
  if(action==='logout'){state.sessions=state.sessions.filter(s=>s!==session);return {body:{},cookie:'',write:true}}
  if(action==='invite'){requireThat(admin);return result({code:invitation(state,body.name?.trim(),body.role)},true)}
  if(action==='changeRole'||action==='renew'){
    requireThat(admin&&body.id!==user.id);
    const target=state.users.find(u=>u.id===body.id&&!u.disabled);requireThat(target);
    if(action==='changeRole'){requireThat(roles.includes(body.role));target.role=body.role}
    else {const code=token();target.invite=hash(code);target.until=Date.now()+86400000;delete target.password;
      state.sessions=state.sessions.filter(s=>s.user!==target.id);return result({code},true)}
    state.sessions=state.sessions.filter(s=>s.user!==target.id);return result({},true);
  }
  if(action==='revoke'){
    requireThat(admin&&(body.id!==user.id||state.users.some(u=>u.id!==user.id&&!u.disabled&&u.role===roles[0]&&(u.password||u.until>Date.now()))));
    const target=state.users.find(u=>u.id===body.id);requireThat(target);
    target.disabled=true;state.sessions=state.sessions.filter(s=>s.user!==target.id);return result({},true);
  }
  if(action==='home')return result({name:user.name,role:user.role,modes,scenarios,
    dossiers:state.dossiers.filter(d=>!d.archived&&((staff&&mine(d))||d.published)).map(d=>({id:d.id,team:d.team,mode:d.mode,scenario:d.scenario,status:staff&&mine(d)?d.status:'Publié',published:!!d.published})),
    users:admin?state.users.map(({id,name,role,disabled})=>({id,name,role,disabled})):[]});
  if(action==='create'){
    requireThat(staff&&modes.includes(body.mode)&&scenarios.includes(body.scenario)&&['Maroc','Portugal'].includes(body.team));
    const items=rows.filter(e=>e.team===body.team&&(e.tags.includes('Perte candidate')===(body.scenario===scenarios[1])));
    const d={id:randomUUID(),owner:user.id,team:body.team,mode:body.mode,scenario:body.scenario,status:'Proposée',version:1,
      items:items.map(e=>({...e,decision:'À examiner',note:''})),history:[]};
    state.dossiers.push(d);return result({id:d.id},true);
  }
  const d=state.dossiers.find(d=>d.id===body.id);
  requireThat(d&&!d.archived,'Dossier inaccessible.',404);
  const edit=staff&&mine(d)&&body.view!=='coach';
  requireThat(edit||d.published,'Dossier inaccessible.',404);
  const record=edit?d:d.published;
  if(action==='detail')return result({id:d.id,team:d.team,mode:d.mode,scenario:d.scenario,status:edit?d.status:'Publié',edit,version:record.version,items:record.items,validation:record.validation,publication:record.publication});
  if(action==='ask'){requireThat(safe(body.q,300),'Question invalide.',400);return result(answer(body.q,record.items))}
  requireThat(edit);
  requireThat(d.version===body.version,'Ce dossier a changé. Rouvrez-le.',409);
  if(action==='archive'&&admin){d.archived=true}
  else if(action==='review'&&['Proposée','Publiée','Validée','Rejetée'].includes(d.status)){d.status='En revue';delete d.validation}
  else if(action==='reject'&&d.status==='En revue'){d.status='Rejetée'}
  else if(action==='mark'&&d.status==='En revue'){
    const e=d.items.find(e=>e.id===body.event);
    requireThat(e&&['Retenue','Écartée','À examiner'].includes(body.decision)&&typeof body.note==='string'&&body.note.length<=1200,'Observation invalide.',400);
    e.decision=body.decision;e.note=body.note.trim();
  }else if(action==='validate'&&d.status==='En revue'&&d.items.some(e=>e.decision==='Retenue')){
    d.validation={author:user.name,date:now()};d.status='Validée';
  }else if(action==='publish'&&d.status==='Validée'){
    d.status='Publiée';d.published={version:d.version+1,validation:{...d.validation},publication:{author:user.name,date:now()},items:structuredClone(d.items.filter(e=>e.decision==='Retenue'))};
  }else requireThat(false,'Transition impossible. Retenez au moins une observation avant validation.',400);
  d.version++;d.history.push({action,author:user.name,date:now(),version:d.version,event:body.event});return result({},true);
}
