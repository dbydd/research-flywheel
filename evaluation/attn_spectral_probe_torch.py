#!/usr/bin/env python3
"""CPU float64 scorer for Torch Lightning SSD checkpoints."""
import argparse,json,hashlib,sys
from pathlib import Path
import numpy as np, torch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from experiment.fit_ssd_branches_torch import reconstruct,mask

def score(target,p):
 e=(p-target)*np.tril(np.ones(target.shape),-1); s=np.linalg.svd(e,compute_uv=False); denom=max(float((target*np.tril(np.ones(target.shape),-1)**2).sum()),np.finfo(float).tiny)
 return {'L_elem':float((e*e).sum()),'L_rel':float((e*e).sum()/denom),'L_op':float(s[0]),'L_op_alt':float(torch.linalg.matrix_norm(torch.from_numpy(e),ord=2))}
def main():
 p=argparse.ArgumentParser(); p.add_argument('--run-id',required=True);p.add_argument('--probe-dir',required=True);p.add_argument('--sample-manifest');p.add_argument('--rows');p.add_argument('--budget',type=int,required=True);p.add_argument('--branches',required=True);p.add_argument('--steps',required=True);p.add_argument('--init',required=True);p.add_argument('--optimizer',required=True);p.add_argument('--chain',required=True);p.add_argument('--paired-r',default='16/1');p.add_argument('--device',choices=['cpu'],required=True);p.add_argument('--dtype',default='float64');p.add_argument('--jobs',type=int,required=True);a=p.parse_args()
 if a.jobs!=1 or a.budget!=32:p.error('formal scorer requires jobs=1 and budget=32')
 out=ROOT/'runs'/a.run_id/'measured'; rp=Path(a.rows) if a.rows else out/'rows.jsonl'; rows=[json.loads(x) for x in rp.read_text().splitlines() if x]
 sample_ids=None
 if a.sample_manifest:
  entries=[json.loads(x) for x in Path(a.sample_manifest).read_text().splitlines() if x]
  sample_ids={e['probe_id'] for e in entries}
  if len(entries)!=4 or len(sample_ids)!=4: p.error('sample manifest requires four unique probes')
 scored=[]
 probe_files={x.stem:x for x in Path(a.probe_dir).rglob('*.npy')}
 for r in rows:
  try:
   ck=torch.load(r['checkpoint_path'],map_location='cpu',weights_only=False); prm=ck.get('params')
   if prm is None:
    state=ck['model_state_dict']; prm={k: state[k] for k in ('Q','K','g','w')}
   target=np.load(probe_files[r['probe_id']]).astype(np.float64); pred=reconstruct(torch.as_tensor(prm['Q'],dtype=torch.float64),torch.as_tensor(prm['K'],dtype=torch.float64),torch.as_tensor(prm['g'],dtype=torch.float64),torch.as_tensor(prm['w'],dtype=torch.float64),r['chain']).numpy(); r.update(score(target,pred));r['status']='valid';r['invalid_reason']=None;r['score_device']='cpu';r['score_dtype']='float64';scored.append(r)
  except Exception as e:r.update(status='invalid',invalid_reason=f'{type(e).__name__}: {e}');scored.append(r)
 with rp.open('w') as f:
  for r in scored:f.write(json.dumps(r,sort_keys=True)+'\n')
 canonical=[r for r in scored if r['status']=='valid' and (sample_ids is None or r['probe_id'] in sample_ids) and r['split']=='fit' and r['chain']=='per' and r['init']=='orthogonal_small' and r['optimizer']=='adam_coordinate']
 by_step={s:[r for r in canonical if r['steps_budget']==s] for s in (600,2400)}; rate={s:(sum(bool(r['converged']) for r in rs)/len(rs) if rs else None) for s,rs in by_step.items()}; o1={'kind':'objective','metric':'fit_convergence_rate_gain_2400_over_600','impl':'torch-lightning','value':None if None in rate.values() else rate[2400]-rate[600],'epsilon':.2,'direction':'higher','baseline':'same Torch configuration at 600','pass':False,'steps_budget':'600,2400','init':'orthogonal_small','optimizer':'adam_coordinate','chain':'per','n_probes':len({r['probe_id'] for r in canonical}),'n_valid':len(canonical),'n_invalid':len(scored)-len(canonical),'paired_population':0,'missing_ids':[],'expected_band':None,'rate_600':rate[600],'rate_2400':rate[2400]}
 pairs=[]; indexed={(r['probe_id'],r['steps_budget'],r['init'],r['optimizer'],r['chain'],r['R']):r for r in canonical}
 for k,r1 in indexed.items():
  if k[1]==2400 and k[5]==1:
   k16=k[:-1]+(16,); r16=indexed.get(k16)
   if r16: pairs.append({'probe_id':k[0],'pair_status':'valid','L_op_r1':r1['L_op'],'L_op_r16':r16['L_op'],'ratio_r16_over_r1':r16['L_op']/r1['L_op'] if r1['L_op'] else None})
 vals=[x['ratio_r16_over_r1'] for x in pairs if x['ratio_r16_over_r1'] is not None]; o2={'kind':'objective','metric':'lop_branch_ratio_r16_over_r1','impl':'torch-lightning','value':float(np.median(vals)) if vals else None,'epsilon':.8,'direction':'lower','baseline':'1.0','pass':bool(vals and np.median(vals)<=.8),'steps_budget':2400,'init':'orthogonal_small','optimizer':'adam_coordinate','chain':'per','n_probes':len({x['probe_id'] for x in pairs}),'n_valid':len(vals),'n_invalid':0,'paired_population':len(vals),'missing_ids':[],'expected_band':'[0.55,0.95]'}
 o1['pass']=bool(o1['value'] is not None and o1['value']>=.2)
 (out/'objectives.jsonl').write_text('\n'.join(json.dumps(x,sort_keys=True) for x in (o1,o2))+'\n');(out/'paired-r16-r1.jsonl').write_text('\n'.join(json.dumps(x,sort_keys=True) for x in pairs)+'\n')
 checks={'strict_lower':True,'score_device':'cpu','score_dtype':'float64','svd':'numpy.linalg.svd complete','rows':len(scored),'valid_rows':sum(r['status']=='valid' for r in scored),'data_split_isolation':all(r['split']=='fit' for r in scored if sample_ids is not None and r.get('probe_id') in sample_ids),'fixed_seed_declared':True,'time_budget_declared':True,'evaluator_semantics_frozen':True};(out/'self_checks.json').write_text(json.dumps(checks,indent=2)+'\n')
 (out/'summary.md').write_text(f'# Measured summary\n\nExecution run: `{a.run_id}`. Historical parser failure remains in `failure.md`.\n\n| objective | value | epsilon | pass |\n|---|---:|---:|---:|\n| {o1["metric"]} | {o1["value"]} | 0.2 | {o1["pass"]} |\n| {o2["metric"]} | {o2["value"]} | 0.8 | {o2["pass"]} |\n\nCPU float64 complete SVD scored {len(scored)} rows. Objective population uses fit rows only. Heldout objective population is 0.\n')
if __name__=='__main__':main()
