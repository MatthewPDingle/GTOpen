from run07 import *
if __name__=='__main__':
    paths=[]
    for opening in (2,3):
        root=[opening,0,0,0,0]
        paths.extend([root,root+[0],root+[1],root+[0,0],root+[1,0],root+[1,1],root+[2],root+[2,0],root+[2,1]])
    for prefix in ([1,0,0,0,0],[1,1,0,0,0],[1,1,1,0,0]):
        paths.extend([prefix,prefix+[0],prefix+[0,0]])
    pathfile=HERE/'broad-paths.json'
    if pathfile.exists():raise RuntimeError('paths already registered')
    pathfile.write_text(json.dumps(paths,indent=2)+'\n',encoding='utf-8',newline='\n')
    run('broad-build-v1',['cargo','build','--release','-p','solver','--features','preflop-research','--example','convergence_audit_paths','--example','convergence_refine_large'])
    exe=LAB/'target/release/examples/convergence_audit_paths.exe'
    for case in ('large-eight-native-local1000','large-eight-sampled-local1000'):
        source=LAB/'target/convergence'/case/'final.gtop'
        run(case+'-broad',[exe,source,pathfile,RAW/(case+'-broad.json')],600,[source,pathfile])
