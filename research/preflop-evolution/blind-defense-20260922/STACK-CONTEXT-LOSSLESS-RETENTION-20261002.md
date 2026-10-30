# Lossless retention and output bounds: 2 October 2026

Transparent NTFS compression passed a complete retained-profile control and an
independent readback. The 809-file native 20bb profile kept every original byte
while using **75.6% less named file allocation** in new compressed directories.
This removes a practical storage obstacle for the next representative cycle;
it does not establish better preflop ranges or a bound for larger runs.

| Quantity | Measured value |
| --- | ---: |
| Original logical and named allocated bytes | 1,278,992,546 |
| Compressed copy named allocated bytes | 311,489,940 |
| Saved named allocated bytes | 967,502,606 |
| Complete copied files, per control | 809 |
| Inherited compressed directories, per control | 33 |
| Corrected control elapsed time | 6.750 s |
| Independent readback elapsed time | 8.578 s |

Two separately named controls retain copies; no historical file was compressed,
linked, overwritten or deleted. The original profile remains unchanged. The
ratio is for this whole measured profile, rather than the earlier zlib samples.
NTFS provides ordinary uncompressed reads to applications. [Microsoft documentation](https://learn.microsoft.com/en-us/windows/win32/fileio/file-compression-and-decompression)

## What was verified

Eight CPU copy workers preserved all original file names and logical SHA-256
hashes. Nested directories inherited compression. A real Python child wrote
native-style stdout and a separate output file into the new store. Reopening,
seeking, appending and renaming preserved the expected bytes. These are software
I/O controls; no native poker calculation, deal generation or fitting occurred.

The first control failed on its final hardlink-accounting test. On this Windows
Python 3.12 fixture, `os.DirEntry.stat(follow_symlinks=False).st_nlink` reported
zero for two names of the same file; `Path.stat()` reported two. The separately
qualified v2 queries `GetFileInformationByHandle`, whose actual link count and
file identity detected both names and refused their storage accounting. The
original failed source, attempt, copies and failure remain preserved. The v2
source comment saying the count can report one does not describe the observed
fixture; the independent audit explicitly qualifies that comment.

The independent audit reconstructed both complete copies and the original
809-file set, all ordinary logical hashes, Win32 compression flags, named
allocation, the v2 per-file manifest, both Python invocation receipts and actual
hardlink fixtures. All 13 source/attempt/failure/result pins agree. It reproduces
v1's false acceptance and v2's refusal. Reparse-path rejection was tested with a
mocked flag, rather than an actual reparse-point fixture.

The helper creates only a new immediate descendant of `S:\GTOpen-research` or
`T:\GTOpen-research`. Existing stores, roots, outside paths and nested-store
requests are refused. New-file accounting refuses hardlinks and reparse points.
Named allocation is the sum of `GetCompressedFileSizeW` values; volume free-space
guards must separately cover filesystem metadata and transient writes. [Windows file information](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/ns-fileapi-by_handle_file_information), [allocation API](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-getcompressedfilesizew)

## Remaining resource admission work

A source-pinned review found three separately written native outputs missing
from current stdout/stderr byte limits: coordinator `queries.json`, worker
`updates.json`, and worker `action-trace.json`. Success and failure receipts must
bind their actual argv paths, presence, logical sizes and hashes, and count them
in the aggregate output budget.

The coordinator can overlap three river and two board workers, so up to **six**
native children can coexist. Proposed 64 MB aggregate transport envelopes and
2 GB board envelopes imply 4.256 GB for those native outputs. Three retained
river stdout copies add 192 MB: 4.448 GB nominal. Unqualified stderr-to-JSON
copying could raise this conservative envelope to 5.408 GB. These are planning
calculations, not measured peaks or admission credit.

Polling regular-file sizes does not prove a transient bound. Prospective
export-only pre-write checks are needed in the bridge, trace and board stdout
serializers, with unchanged JSON bytes/newline behavior and qualified source
and executable identities. The existing river exporter already checks its
serialized stdout length; status stdout and diagnostic stderr still need joint
accounting. No such prospective source or executable was modified here.

After complete output and overshoot qualification, refresh global storage
accounting and admit one full cycle across 20/40/100/200/400bb. The static proxy
of roughly 18 GB raw storage remains unmeasured; this retention ratio must not
be treated as guaranteed for that larger cycle. Only after representative
resource measurements should the stability comparison's board sampling,
independent runs and fresh payoff evaluation be registered.

The original failed improvement finding remains unchanged. Five-bets,
stack-appropriate opening ranges, other positions, multiway accuracy, GTO Wizard
comparisons and production readiness remain outstanding. Production on 56708
was not changed, and nothing was pushed to GitHub or deployed.
