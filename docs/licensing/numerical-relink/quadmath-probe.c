/* Local source-rebuild check, 2026-10-26. Distributed under MIT. */
#include <stdio.h>
#include <string.h>
#include <quadmath.h>

extern const char *procgen_quadmath_relink_probe(void);

int main(void)
{
    char result[128];
    __float128 x = strtoflt128("2.0", NULL);
    if (quadmath_snprintf(result, sizeof(result), "%.30Qg", sqrtq(x)) <= 0)
        return 1;
    if (strncmp(result, "1.41421356237309504880168872421", 31) != 0)
        return 2;
    puts(procgen_quadmath_relink_probe());
    puts(result);
    return 0;
}
