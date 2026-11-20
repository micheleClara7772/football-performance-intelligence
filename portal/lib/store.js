import {get, put, head, BlobNotFoundError, BlobServiceRateLimited, BlobServiceNotAvailable} from '@vercel/blob';
const path='portal/state-v1.json';
function transient(error){
  return error instanceof BlobServiceRateLimited || error instanceof BlobServiceNotAvailable;
}
async function withBackoff(op){
  for(let attempt=0;;attempt++){
    try{return await op()}catch(error){
      if(attempt>=2||!transient(error))throw error;
      await new Promise(done=>setTimeout(done,Math.min(3500,Math.max(700*(attempt+1),(error.retryAfter||0)*1000))));
    }
  }
}
export async function read(){
  let meta;
  try{meta=await withBackoff(()=>head(path))}
  catch(error){if(error instanceof BlobNotFoundError)return {users:[],sessions:[],dossiers:[]};throw error}
  const result=await withBackoff(()=>get(path,{access:'private',useCache:false,headers:{'accept-encoding':'identity'}}));
  if(!result)return {users:[],sessions:[],dossiers:[]};
  const state=await new Response(result.stream).json();
  state.etag=meta.etag;
  return state;
}
export async function persist(state){
  const {etag,...data}=state;
  await withBackoff(()=>put(path,JSON.stringify(data),{
    access:'private',addRandomSuffix:false,...(etag?{ifMatch:etag}:{}),
  }));
}
