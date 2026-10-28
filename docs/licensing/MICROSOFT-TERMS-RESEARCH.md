# Microsoft runtime terms research — 2026-10-26

## Update 2026-10-28: current implementation supersedes the original selection

The installed VS2019 CRT14.29 is too old for dependencies linked with14.51,
even though exported symbol coverage passed. The current build uses the
**official stable VC14 14.51.36247.0 x64 download** under the installed
**Community2022** license, whose section4 (not the 2019 license's section3)
grants application distribution. The [2022 REDIST list](https://learn.microsoft.com/en-us/visualstudio/releases/2022/redistribution)
expressly includes individual binaries obtained from the latest-supported
runtime page for licensed Visual Studio users. Its [latest-supported page](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist?view=msvc-170)
recommends that shared v14 family for VS2019/2022 applications. Community's
open-source exception applies to this MIT project. Original 2022 terms,
provenance, exact versions/hashes/signatures, non-executing extraction and
toolset-floor checks are documented in [MICROSOFT-RUNTIME.md](MICROSOFT-RUNTIME.md).
The previously built VS2019 /MD GLFW3.3.2 DLL is retained unchanged.

The original investigation below records why a standalone installation/use
EULA is not itself a redistribution grant. That distinction remains valid;
the explicit licensed-Visual-Studio download route above now supplies the
current source selection. Historical 2019 source-selection recommendations
below are superseded, not instructions to stage an older CRT.

## Original 2026-10-26 investigation

Use the **installed Visual Studio Community 2019 redistributable directory**
as the explicit VC14 source, with its EULA, REDIST reference, file versions,
hashes and signatures preserved. Session evidence establishes an independent
MIT open-source project and an installed Community 2019 toolchain. The
Community open-source use provision applies without an organization-size
question. This is a project-specific application of the terms, not a claim
that every download of a Microsoft runtime grants redistribution rights.

Rebuild the unchanged GLFW 3.3.2 source with that toolchain to eliminate its
VC11 dependency if practical. Keep Windows 10/11's UCRT/API sets system-provided.
Do not treat an arbitrary DLL found on PATH as an authorized source.

## Community 2019: the concrete redistribution route

The [official Community 2019 EULA page](https://visualstudio.microsoft.com/license-terms/mlt031819/)
links this [English license document](https://visualstudio.microsoft.com/wp-content/uploads/2020/05/VS_Community_2019_ENU.1033.docx),
EULA ID `VS_Community_2019_ENU.1033`. It permits individual own-application
development and organizational development/testing of applications released
under OSI-approved licenses. Its enterprise exception preserves that
open-source use. Section 3 permits object-code distribution from the REDIST
list and permits downstream distributors to redistribute it as part of the
application. Conditions include significant primary functionality and
protective terms agreed by distributors and external end users. Microsoft
notices must remain; its trademarks must not imply endorsement. Its
Excluded-License restriction concerns making the Microsoft code itself
subject to source-disclosure/modification obligations. These conditions are
component-specific; our own code can retain MIT.

The [2019 REDIST list](https://learn.microsoft.com/en-us/visualstudio/releases/2019/redistribution)
explicitly names Community 2019 among the applicable editions. Under the
Visual C++ runtime section it allows unmodified files from `VC/redist` and
subdirectories, except `debug_nonredist`. That list is used together with the
EULA, rather than as an independent license grant. Thus ordinary release
`x64/Microsoft.VC142.CRT` files in the installed toolchain have a documented
route; arbitrary files outside that provenance do not acquire it by sharing
the same filename.

**Implementation condition:** a notice file alone is not evidence that an
end user agreed to protective terms. Provide component-scoped downstream
Microsoft terms and an appropriate agreement process before public binary
distribution. The MIT license for the launcher must not purport to relicense
the Microsoft DLLs. No additional organizational entitlement question is
needed on the established open-source facts.

## Standalone runtime downloads are not the grant

[Microsoft's deployment documentation](https://learn.microsoft.com/en-us/cpp/windows/redistributing-visual-cpp-files)
limits redistribution of packages and individual binaries to licensed Visual
Studio users under the applicable software terms. It documents app-local
DLL deployment but prefers centralized servicing; deployment feasibility is
separate from permission.

The [2015–2022 runtime EULA](https://visualstudio.microsoft.com/license-terms/vs2022-cruntime/)
links [the actual DOCX](https://visualstudio.microsoft.com/wp-content/uploads/2021/09/Visual-C-Runtime-2015-2022-License-1.docx),
ID `Cpp_2015-2022_ENU.1033`. Its standalone rights are installation/use;
its scope section prohibits sharing/publishing and providing the software
combined with an application for others. It therefore does **not**, by
itself, authorize extracting and shipping DLLs with our ZIP.

The [2015 add-ons/runtime terms](https://visualstudio.microsoft.com/license-terms/mt171552/)
and [2017 tools/add-ons/runtime terms](https://visualstudio.microsoft.com/license-terms/mlt552233/)
also grant installation/use and restrict sharing/publishing. Their utilities
provisions are not a blanket runtime redistribution grant. The
[2026 v14 runtime terms](https://visualstudio.microsoft.com/license-terms/vs2026-ga-visualcpp-v14-redist-runtime/)
likewise expressly prohibit redistribution in their standalone scope. Merely
switching to the newest `vc_redist` download does not solve this question.

## VC11 / Visual Studio 2012

The [2012 REDIST list](https://learn.microsoft.com/en-us/visualstudio/releases/2012/2012-redistribution-vs)
includes x64 `msvcr110.dll` under `Microsoft.VC110.CRT`, and has a separate
Express 2012 for Windows Desktop section. These are expressly subject to the
applicable Visual Studio license. A VS2019 installation does not, from that
source alone, establish the separate VS2012 entitlement. The exact Update 4
standalone installer EULA was not recovered from a first-party document in
this research pass; third-party reproductions were not used as authority.
Preserving its DLL from a wheel or downloading it alone cannot be treated as
proof of a redistribution grant.

The concrete cleanup is to avoid distributing VC11: rebuild GLFW 3.3.2 using
the established Community 2019 route and verify its PE imports no longer
include `MSVCR110.dll`. If VC11 is retained instead, preserve its exact signed
official package/EULA and establish a valid VS2012 redistribution route.

## CPython's Windows notice

The pinned [CPython 3.10.1 `PC/crtlicense.txt`](https://github.com/python/cpython/blob/v3.10.1/PC/crtlicense.txt)
matches the Microsoft section in our installed Python license. It says
redistributing the Windows interpreter build complies when Microsoft notices
are retained, names do not imply Microsoft endorsement, Microsoft code stays
on Microsoft platforms, and the program is not malicious/deceptive/unlawful.
It also requires distributors and external end users to agree to sufficiently
protective Microsoft-code terms. These restrictions apply to that Microsoft
code, not to Python itself or programs running on Python. This supports
preserving the interpreter's original build and notice; it is **not a blanket
grant for unrelated `msvcp140.dll` or GLFW's VC11 DLL found elsewhere**.

## Windows 10/11 UCRT and API sets

[Microsoft UCRT deployment documentation](https://learn.microsoft.com/en-us/cpp/windows/universal-crt-deployment)
identifies the UCRT as an operating-system component included in Windows 10+
and says Windows 10/11 always uses the system UCRT, even if an app-local copy
is newer. For this project's Windows 10/11 target, omitting app-local
`ucrtbase.dll` and UCRT forwarders avoids unnecessary redistributable payload.
Do not extend that conclusion to older Windows targets.

[API-set documentation](https://learn.microsoft.com/en-us/windows/win32/apiindex/windows-apisets)
explains that an API-set name identifies a contract resolved by Windows'
loader/schema, rather than necessarily a physical DLL. Therefore dependency
import names such as `api-ms-win-*` are not sufficient justification to copy
similarly named files from an unrelated PATH directory.

[Microsoft's binary compatibility rules](https://learn.microsoft.com/en-us/cpp/porting/binary-compat-2015-2017)
require a redistributable at least as new as the latest build tools used by
any application component. Select a coherent authorized runtime source and
verify native imports and actual versions; don't infer suitability from the
`140` suffix alone. Full isolated native and final desktop testing still apply.

## Research artifacts

Official EULA DOCX files and extracted reading text were downloaded only into
ignored `.artifacts/microsoft-terms/`. No installer was run, system runtime
was changed, account was accessed, or third party contacted. The controlled
runtime packaging manifest should preserve selected files independently of
this temporary research directory.

| Local research document | SHA-256 |
| --- | --- |
| `vs2019-community.docx` | `3dc17ec1490b436a97816aa4b06cc08eac9e37933a2813dbfa1886eaf23bde08` |
| `vc-runtime-license.docx` | `f1e3d56ceb2ad68aae0711b910375009e651ac5530fa0760f0dea6e81e54fae1` |
| `v14-2026.docx` | `08651651a7602fc7c0e2763de0fde1ff9f868df2780597cd1775ee9d6441c783` |
| `vs2017-runtime.docx` | `d6a607da4bb74068bd6a80fc1addc4aaaae673b530a085864fb718bf20a66f8c` |
