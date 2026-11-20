import {BlobPreconditionFailedError} from '@vercel/blob';
import {serve} from '../lib/service.js';
import {read,persist} from '../lib/store.js';
export default async function handler(req,res){
  res.setHeader('Cache-Control','private, no-store');
  if(req.method!=='POST'||!req.headers['content-type']?.startsWith('application/json')||req.headers['x-fpi']!=='1')return res.status(405).json({error:'Requête invalide.'});
  try{
    const key=(req.headers.cookie||'').match(/(?:^|; )fpi_session=([\w-]+)/)?.[1];
    const state=await read();const result=serve(state,req.body,key,process.env.FPI_BOOTSTRAP_HASH);
    if(result.write)await persist(state);
    if(result.cookie!==undefined)res.setHeader('Set-Cookie','fpi_session='+result.cookie+'; HttpOnly; Secure; SameSite=Strict; Path=/; Max-Age='+(result.cookie?28800:0));
    res.status(200).json(result.body);
  }catch(e){
    const conflict=e instanceof BlobPreconditionFailedError;
    if(!e.status&&!conflict)console.error('FPI request failed',e.constructor.name);
    res.status(e.status||(conflict?409:503)).json({error:e.status?e.message:conflict?'Modification simultanée. Rechargez le dossier.':'Stockage temporairement indisponible.'});
  }
}
