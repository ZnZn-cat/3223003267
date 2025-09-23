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

int main(int argc, char *argv[]){
    if (argc != 4) {
        printf("Usage: %s original_file plagiarized_file output_file\n", argv[0]);
        return 1;
    }

    const char *orig_path = argv[1];
    const char *plag_path = argv[2];
    const char *output_path = argv[3];

    // 设置locale以支持UTF-8
    setlocale(LC_ALL, "en_US.UTF-8");

    // 读取原文文件
    FILE *orig_file = fopen(orig_path, "rb");
    if (orig_file == NULL) {
        perror("Failed to open original file");
        return 1;
    }
    fseek(orig_file, 0, SEEK_END);
    long orig_size = ftell(orig_file);
    fseek(orig_file, 0, SEEK_SET);
    char *orig_text = (char *)malloc(orig_size + 1);
    if (orig_text == NULL) {
        perror("malloc");
        fclose(orig_file);
        return 1;
    }
    size_t read_size = fread(orig_text, 1, orig_size, orig_file);
    orig_text[read_size] = '\0';
    fclose(orig_file);
    // 读取抄袭版文件
    FILE *plag_file = fopen(plag_path, "rb");
    if (plag_file == NULL) {
        perror("Failed to open plagiarized file");
        free(orig_text);
        return 1;
    }
    fseek(plag_file, 0, SEEK_END);
    long plag_size = ftell(plag_file);
    fseek(plag_file, 0, SEEK_SET);
    char *plag_text = (char *)malloc(plag_size + 1);
    if (plag_text == NULL) {
        perror("malloc");
        fclose(plag_file);
        free(orig_text);
        return 1;
    }
    read_size = fread(plag_text, 1, plag_size, plag_file);
    plag_text[read_size] = '\0';
    fclose(plag_file);

    // 转换多字节字符串为宽字符串
    size_t orig_wide_len = mbstowcs(NULL, orig_text, 0);
    size_t plag_wide_len = mbstowcs(NULL, plag_text, 0);
    if (orig_wide_len == (size_t)-1 || plag_wide_len == (size_t)-1) {
        perror("mbstowcs failed");
        free(orig_text);
        free(plag_text);
        return 1;
    }
    wchar_t *orig_wide = (wchar_t *)malloc((orig_wide_len + 1) * sizeof(wchar_t));
    wchar_t *plag_wide = (wchar_t *)malloc((plag_wide_len + 1) * sizeof(wchar_t));
    if (orig_wide == NULL || plag_wide == NULL) {
        perror("malloc wide string");
        free(orig_text);
        free(plag_text);
        if (orig_wide) free(orig_wide);
        if (plag_wide) free(plag_wide);
        return 1;
    }
    mbstowcs(orig_wide, orig_text, orig_wide_len + 1);
    mbstowcs(plag_wide, plag_text, plag_wide_len + 1);

    // 计算LCS长度
    size_t lcs_len = lcs_length(orig_wide, plag_wide, orig_wide_len, plag_wide_len);

    // 计算重复率
    double rate;
    if (orig_wide_len == 0) {
        rate = 0.0;
    } else {
        rate = (double)lcs_len / orig_wide_len;
    }

    // 输出重复率到文件
    FILE *output_file = fopen(output_path, "w");
    if (output_file == NULL) {
        perror("Failed to open output file");
        free(orig_text);
        free(plag_text);
        free(orig_wide);
        free(plag_wide);
        return 1;
    }
    fprintf(output_file, "%.2f", rate);
    fclose(output_file);

    // 释放内存
    free(orig_text);
    free(plag_text);
    free(orig_wide);
    free(plag_wide);

    return 0;
}
