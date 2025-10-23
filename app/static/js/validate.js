const CanaryFormValidator = (() => {
    function validate(form) {
        const headerValue = form.header_value.value.trim();
        const headerPattern = form.header_pattern.value.trim();
        const weight = parseInt(form.weight.value, 10);

        if (headerValue && headerPattern) {
            alert("canary-by-header-value 和 canary-by-header-pattern 不能同时设置");
            return false;
        }

        if (headerPattern) {
            try {
                new RegExp(headerPattern);
            } catch(e) {
                alert("canary-by-header-pattern 正则格式错误: " + e.message);
                return false;
            }
        }

        if (isNaN(weight) || weight < 0 || weight > 100) {
            alert("canary-weight 必须是 0-100 的整数");
            return false;
        }

        return true;
    }

    return { validate };
})();