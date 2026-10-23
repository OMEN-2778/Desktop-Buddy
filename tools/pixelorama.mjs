// Call the installed MCP server from Codex without changing global client config.
import {dirname,join} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {mkdirSync,writeFileSync} from 'node:fs';
const repo=dirname(dirname(fileURLToPath(import.meta.url)));
const root=process.env.PIXELORAMA_ROOT||join(dirname(repo),'extra-tools');
const sdk=join(root,'Pixelorama-MCP/mcp-server/node_modules/@modelcontextprotocol/sdk/dist/esm/client');
const {Client}=await import(pathToFileURL(join(sdk,'index.js')));
const {StdioClientTransport}=await import(pathToFileURL(join(sdk,'stdio.js')));
const tool=process.argv[2];if(!tool)throw Error('Usage: node tools/pixelorama.mjs TOOL JSON_ARGUMENTS');
const c=new Client({name:'desktop-buddy-art',version:'1.0'});
try{
 await c.connect(new StdioClientTransport({command:'bash',args:[join(repo,'tools/pixelorama.sh'),'mcp']}));
 const r=await c.callTool({name:tool,arguments:JSON.parse(process.argv[3]||'{}')});
 const out=join(dirname(repo),'artifacts/pixelorama');mkdirSync(out,{recursive:true});
 for(const item of r.content||[]){
  if(item.type==='image'){const path=join(out,tool+'.png');writeFileSync(path,Buffer.from(item.data,'base64'));console.log('Image:',path);}
  else if(item.type==='text'){
   if(item.text.length>2500){const path=join(out,tool+'.json');writeFileSync(path,item.text);console.log('Result:',path);}
   else console.log(item.text);
  }
 }
 if(r.isError)process.exitCode=1;
}finally{await c.close();}
