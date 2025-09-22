#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <wchar.h>
#include <locale.h>

#define max(a, b) ((a) > (b) ? (a) : (b))

// 计算两个宽字符串的最长公共子序列长度
size_t lcs_length(const wchar_t *X, const wchar_t *Y, size_t m, size_t n) {
    size_t *dp = (size_t *)malloc((n + 1) * sizeof(size_t));
    if (dp == NULL) {
        perror("malloc");
        exit(1);
    }
    for (size_t j = 0; j <= n; j++) {
        dp[j] = 0;
    }

    for (size_t i = 0; i < m; i++) {
        size_t prev = 0;
        for (size_t j = 0; j < n; j++) {
            size_t temp = dp[j + 1];
            if (X[i] == Y[j]) {
                dp[j + 1] = prev + 1;
            } else {
                dp[j + 1] = max(dp[j + 1], dp[j]);
            }
            prev = temp;
        }
    }

    size_t result = dp[n];
    free(dp);
    return result;
}

int main(){

    
}