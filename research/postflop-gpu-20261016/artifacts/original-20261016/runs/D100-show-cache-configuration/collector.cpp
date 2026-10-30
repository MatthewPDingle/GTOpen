// Private diagnostic collector. Explicit lifetime, no exit hooks or system changes.
#include <windows.h>
#include <cupti.h>
#include <atomic>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cstdint>
#include <malloc.h>
#include <io.h>
#include <fcntl.h>
#include <share.h>
#include <sys/stat.h>

#pragma pack(push,1)
struct Row {
    uint32_t kind, device, context, stream, correlation, detail;
    uint64_t start, end, bytes, graphNode;
    uint32_t graph, grid[3], block[3], regs, staticShared, dynamicShared;
    char name[80];
};
#pragma pack(pop)
static_assert(sizeof(Row)==176,"trace schema");
static SRWLOCK fileLock=SRWLOCK_INIT;
static FILE *traceFile=nullptr,*metaFile=nullptr;
static CUpti_SubscriberHandle subscriber=nullptr;
static std::atomic<uint64_t> errors{0},dropped{0},rows{0},kernels{0},copies{0},sets{0},apis{0},badTimes{0},outstanding{0},peak{0};
static bool enabled[4]={false,false,false,false};
static const CUpti_ActivityKind kinds[4]={CUPTI_ACTIVITY_KIND_CONCURRENT_KERNEL,CUPTI_ACTIVITY_KIND_MEMCPY,CUPTI_ACTIVITY_KIND_MEMSET,CUPTI_ACTIVITY_KIND_DRIVER};
static int state=0;
static bool check(CUptiResult rc,const char *operation) {
    if(rc==CUPTI_SUCCESS)return true;
    errors.fetch_add(1);
    AcquireSRWLockExclusive(&fileLock);
    if(metaFile){fprintf(metaFile,"{\"event\":\"error\",\"operation\":\"%s\",\"code\":%u}\n",operation,(unsigned)rc);fflush(metaFile);}
    ReleaseSRWLockExclusive(&fileLock);return false;
}
static FILE *exclusiveFile(const wchar_t *env) {
    wchar_t path[32768];DWORD n=GetEnvironmentVariableW(env,path,32768);if(!n||n>=32768)return nullptr;
    int fd=-1;if(_wsopen_s(&fd,path,_O_CREAT|_O_EXCL|_O_BINARY|_O_WRONLY,_SH_DENYWR,_S_IREAD|_S_IWRITE)!=0)return nullptr;
    FILE *f=_wfdopen(fd,L"wb");if(!f)_close(fd);return f;
}
static void CUPTIAPI callback(void *,CUpti_CallbackDomain,CUpti_CallbackId,const void *) {}
static void CUPTIAPI requestBuffer(uint8_t **buffer,size_t *size,size_t *maxRecords) {
    uint64_t now=outstanding.fetch_add(1)+1,prior=peak.load();while(prior<now&&!peak.compare_exchange_weak(prior,now)){}
    *maxRecords=0;*size=2*1024*1024;
    if(now>64){outstanding.fetch_sub(1);errors.fetch_add(1);*buffer=nullptr;*size=0;return;}
    *buffer=(uint8_t*)_aligned_malloc(*size,8);if(!*buffer){outstanding.fetch_sub(1);errors.fetch_add(1);*size=0;}
}
static void CUPTIAPI completeBuffer(CUcontext context,uint32_t stream,uint8_t *buffer,size_t size,size_t valid) {
    (void)size;CUpti_Activity *activity=nullptr;CUptiResult rc=CUPTI_SUCCESS;
    while(valid&&(rc=cuptiActivityGetNextRecord(buffer,valid,&activity))==CUPTI_SUCCESS){
        Row row{};row.kind=(uint32_t)activity->kind;
        if(activity->kind==CUPTI_ACTIVITY_KIND_KERNEL||activity->kind==CUPTI_ACTIVITY_KIND_CONCURRENT_KERNEL){
            auto *a=(CUpti_ActivityKernel9*)activity;
            row.device=a->deviceId;row.context=a->contextId;row.stream=a->streamId;row.correlation=a->correlationId;
            row.start=a->start;row.end=a->end;row.graphNode=a->graphNodeId;row.graph=a->graphId;
            row.grid[0]=a->gridX;row.grid[1]=a->gridY;row.grid[2]=a->gridZ;row.block[0]=a->blockX;row.block[1]=a->blockY;row.block[2]=a->blockZ;
            row.regs=a->registersPerThread;row.staticShared=a->staticSharedMemory;row.dynamicShared=a->dynamicSharedMemory;
            row.detail=uint32_t(a->cacheConfig.both)|(uint32_t(a->isSharedMemoryCarveoutRequested)<<8)|(uint32_t(a->sharedMemoryCarveoutRequested)<<16);row.bytes=a->sharedMemoryExecuted;
            if(a->name){if(strlen(a->name)>=sizeof(row.name))errors.fetch_add(1);strncpy_s(row.name,a->name,_TRUNCATE);}kernels.fetch_add(1);
        }else if(activity->kind==CUPTI_ACTIVITY_KIND_MEMCPY){
            auto *a=(CUpti_ActivityMemcpy6*)activity;
            row.device=a->deviceId;row.context=a->contextId;row.stream=a->streamId;row.correlation=a->correlationId;row.detail=a->copyKind;
            row.start=a->start;row.end=a->end;row.bytes=a->bytes;row.graphNode=a->graphNodeId;row.graph=a->graphId;copies.fetch_add(1);
        }else if(activity->kind==CUPTI_ACTIVITY_KIND_MEMSET){
            auto *a=(CUpti_ActivityMemset4*)activity;
            row.device=a->deviceId;row.context=a->contextId;row.stream=a->streamId;row.correlation=a->correlationId;row.detail=a->value;
            row.start=a->start;row.end=a->end;row.bytes=a->bytes;row.graphNode=a->graphNodeId;row.graph=a->graphId;sets.fetch_add(1);
        }else if(activity->kind==CUPTI_ACTIVITY_KIND_DRIVER){
            auto *a=(CUpti_ActivityAPI*)activity;
            row.context=a->processId;row.stream=a->threadId;row.correlation=a->correlationId;row.detail=a->cbid;
            row.start=a->start;row.end=a->end;row.graph=a->returnValue;apis.fetch_add(1);
        }else {errors.fetch_add(1);continue;}
        if(!row.start||row.end<row.start)badTimes.fetch_add(1);
        AcquireSRWLockExclusive(&fileLock);
        if(!traceFile||fwrite(&row,sizeof(row),1,traceFile)!=1)errors.fetch_add(1);
        ReleaseSRWLockExclusive(&fileLock);rows.fetch_add(1);
    }
    if(valid&&rc!=CUPTI_ERROR_MAX_LIMIT_REACHED)check(rc,"get_next_record");
    size_t count=0;if(check(cuptiActivityGetNumDroppedRecords(context,stream,&count),"get_dropped_records"))dropped.fetch_add(count);
    _aligned_free(buffer);outstanding.fetch_sub(1);
}
// Host phase timestamp in CUPTI's activity time domain, diagnostic only.
extern "C" __declspec(dllexport) uint32_t D100PhaseTrace(uint32_t marker) {
    if(state!=1||!metaFile)return 0;
    uint64_t timestamp=0;if(!check(cuptiGetTimestamp(&timestamp),"phase_timestamp")||!timestamp)return 0;
    AcquireSRWLockExclusive(&fileLock);
    fprintf(metaFile,"{\"event\":\"phase\",\"marker\":%u,\"timestamp_ns\":%llu}\n",marker,(unsigned long long)timestamp);fflush(metaFile);
    ReleaseSRWLockExclusive(&fileLock);return errors.load()==0;
}
extern "C" __declspec(dllexport) uint32_t D100StartTrace() {
    if(state!=0)return state==1&&errors.load()==0;
    state=1;traceFile=exclusiveFile(L"D100_TRACE_FILE");metaFile=exclusiveFile(L"D100_META_FILE");
    if(!traceFile||!metaFile){errors.fetch_add(1);return 0;}
    setvbuf(traceFile,nullptr,_IOFBF,1024*1024);
    const char magic[16]={'D','1','0','0','-','T','R','A','C','E','-','v','1',0,0,0};
    if(fwrite(magic,sizeof(magic),1,traceFile)!=1){errors.fetch_add(1);return 0;}
    // Subscribe before other CUPTI calls. No performance-counter APIs requested.
    if(!check(cuptiSubscribe(&subscriber,callback,nullptr),"subscribe"))return 0;
    uint32_t version=0;if(!check(cuptiGetVersion(&version),"get_version"))return 0;
    fprintf(metaFile,"{\"event\":\"start\",\"cupti_api_version\":%u,\"row_bytes\":%zu,\"kernel_struct_bytes\":%zu,\"buffer_bytes\":2097152,\"max_buffers\":64,\"explicit_lifetime\":true,\"hardware_counters\":false}\n",version,sizeof(Row),sizeof(CUpti_ActivityKernel9));fflush(metaFile);
    if(!check(cuptiActivityRegisterCallbacks(requestBuffer,completeBuffer),"register_callbacks"))return 0;
    for(int i=0;i<4;i++){if(!check(cuptiActivityEnable(kinds[i]),"enable_activity"))return 0;enabled[i]=true;}
    return errors.load()==0;
}
extern "C" __declspec(dllexport) uint32_t D100FlushTrace() {
    if(state!=1||!subscriber)return 0;
    check(cuptiActivityFlushAll(0),"flush_completed");return errors.load()==0;
}
extern "C" __declspec(dllexport) uint32_t D100StopTrace() {
    if(state==2)return errors.load()==0&&dropped.load()==0&&badTimes.load()==0;
    if(state==0)return 1;
    // Called explicitly while the diagnostic still owns its CUDA context.
    for(int i=0;i<4;i++)if(enabled[i]){check(cuptiActivityDisable(kinds[i]),"disable_activity");enabled[i]=false;}
    if(subscriber){check(cuptiActivityFlushAll(CUPTI_ACTIVITY_FLAG_FLUSH_FORCED),"flush_forced");check(cuptiUnsubscribe(subscriber),"unsubscribe");subscriber=nullptr;check(cuptiFinalize(),"finalize_after_synchronization_and_flush");}
    AcquireSRWLockExclusive(&fileLock);
    if(traceFile){if(fflush(traceFile)!=0||ferror(traceFile))errors.fetch_add(1);fclose(traceFile);traceFile=nullptr;}
    if(metaFile){fprintf(metaFile,"{\"event\":\"complete\",\"records\":%llu,\"kernels\":%llu,\"memcopies\":%llu,\"memsets\":%llu,\"driver_api_records\":%llu,\"dropped\":%llu,\"errors\":%llu,\"invalid_timestamps\":%llu,\"outstanding_buffers\":%llu,\"peak_buffers\":%llu}\n",rows.load(),kernels.load(),copies.load(),sets.load(),apis.load(),dropped.load(),errors.load(),badTimes.load(),outstanding.load(),peak.load());fflush(metaFile);fclose(metaFile);metaFile=nullptr;}
    ReleaseSRWLockExclusive(&fileLock);state=2;return errors.load()==0&&dropped.load()==0&&badTimes.load()==0;
}
