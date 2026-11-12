import {createRequire} from 'module';const require=createRequire('/opt/npm-tools/node_modules/');
const {chromium}=require('playwright');const b=await chromium.launch();const p=await b.newPage();
p.on('pageerror',e=>console.log('PAGEERR '+e.message+'\n'+(e.stack||'').split('\n').slice(0,4).join('\n')));p.on('console',m=>{if(m.type()==='error')console.log('ERR',m.text().slice(0,300))});
await p.goto('http://localhost:8765/index.html');await p.waitForTimeout(1500);console.log(await p.evaluate(()=>typeof __G));await b.close();
