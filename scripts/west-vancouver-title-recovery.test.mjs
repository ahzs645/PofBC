import test from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { gunzipSync } from 'node:zlib'
import { applyWestVancouverTitleRecovery } from './lib/west-vancouver-title-recovery.mjs'
const dir = new URL('../research/salaries/', import.meta.url)
const corrections = JSON.parse(readFileSync(new URL('west-vancouver-title-recovery/corrections.json', dir)))
const sources = JSON.parse(readFileSync(new URL('municipal-lower-mainland/sources.json', dir))).sources.filter(s => corrections.some(c => c.sourceId === s.id))
const rows = sources.flatMap(s => JSON.parse(gunzipSync(readFileSync(new URL('municipal-lower-mainland/' + s.file, dir)))).map(([slug,name,position,pay,expenses,page]) => ({slug,year:s.year,name,position,pay,expenses,page,sourceId:s.id})))
test('1752 title corrections preserve every other field and count', () => {
 const result=applyWestVancouverTitleRecovery(rows,corrections)
 assert.equal(result.length,1752)
 for(let i=0;i<rows.length;i++) { const {name,position,...rest}=result[i]; const {name:oldName,position:oldPosition,...before}=rows[i]; assert.deepEqual(rest,before); assert.ok(position); assert.notEqual(name,oldName) }
})
test('changed amount, name, page, ordering, missing and duplicate rows fail closed',()=> {
 for(const field of ['name','pay','expenses','page','year','sourceId']) { const changed=structuredClone(rows);changed[0][field]='tampered'; assert.throws(()=>applyWestVancouverTitleRecovery(changed,corrections)) }
 assert.throws(()=>applyWestVancouverTitleRecovery(rows.slice(1),corrections))
 assert.throws(()=>applyWestVancouverTitleRecovery([...rows,rows[0]],corrections))
 const reordered=rows.slice(); [reordered[0],reordered[1]]=[reordered[1],reordered[0]];assert.throws(()=>applyWestVancouverTitleRecovery(reordered,corrections))
})

test('inverse restores exact packed observations for historical replay',async()=> {
 const {reverseWestVancouverTitleRecovery}=await import('./lib/west-vancouver-title-recovery.mjs')
 const index={employers:[[null,null,null,'district-of-west-vancouver']],years:['2019','2022','2023','2024']}
 const pack=r=>[r.name,r.position,r.pay,r.expenses,0,index.years.indexOf(r.year),r.sourceId,r.page]
 const corrected=applyWestVancouverTitleRecovery(rows,corrections).map(pack)
 assert.deepEqual(reverseWestVancouverTitleRecovery(corrected,index,corrections),rows.map(pack))
 corrected[0][2]++;assert.throws(()=>reverseWestVancouverTitleRecovery(corrected,index,corrections))
})
