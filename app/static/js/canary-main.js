// Canary Controller Main JavaScript
// 整合了Toast系统、输入框展开和表单处理

console.log('Canary Main JavaScript loading...');

// Toast通知系统
const SimpleToast = {
    container: null,

    init() {
        console.log('Toast init...');
        if (!this.container) {
            this.container = document.createElement('div');
            this.container.className = 'toast-container';
            this.container.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 9999;
                max-width: 350px;
            `;
            document.body.appendChild(this.container);
            console.log('Toast container created');
        }
    },

    show(message, type = 'info', duration = 3000) {
        console.log('Showing toast:', message, type);
        this.init();

        const toast = document.createElement('div');
        toast.style.cssText = `
            min-width: 250px;
            margin-bottom: 10px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            padding: 12px 16px;
            color: white;
            font-size: 14px;
            animation: slideIn 0.3s ease-out;
        `;

        // 设置背景色
        if (type === 'success') {
            toast.style.background = 'linear-gradient(135deg, #28a745 0%, #20c997 100%)';
        } else if (type === 'error') {
            toast.style.background = 'linear-gradient(135deg, #dc3545 0%, #fd7e14 100%)';
        } else if (type === 'warning') {
            toast.style.background = 'linear-gradient(135deg, #ffc107 0%, #fd7e14 100%)';
            toast.style.color = '#212529';
        } else {
            toast.style.background = '#6c757d';
        }

        toast.textContent = message;
        this.container.appendChild(toast);

        // 添加动画
        if (!document.getElementById('toast-animations')) {
            const style = document.createElement('style');
            style.id = 'toast-animations';
            style.textContent = `
                @keyframes slideIn {
                    from { transform: translateX(100%); opacity: 0; }
                    to { transform: translateX(0); opacity: 1; }
                }
                @keyframes slideOut {
                    from { transform: translateX(0); opacity: 1; }
                    to { transform: translateX(100%); opacity: 0; }
                }
                .toast-hide {
                    animation: slideOut 0.3s ease-out forwards;
                }
            `;
            document.head.appendChild(style);
        }

        // 自动隐藏
        setTimeout(() => {
            toast.classList.add('toast-hide');
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
            }, 300);
        }, duration);
    },

    success(message, duration = 3000) {
        this.show(message, 'success', duration);
    },

    error(message, duration = 5000) {
        this.show(message, 'error', duration);
    },

    warning(message, duration = 4000) {
        this.show(message, 'warning', duration);
    }
};

// 输入框展开管理
const InputExpander = {
    expandedInputs: new Set(),

    init() {
        console.log('Input expander init...');
        this.setupInputListeners();
        this.setupKeyboardListeners();
    },

    setupInputListeners() {
        document.addEventListener('focus', (e) => {
            if (e.target.matches('.input-expandable')) {
                this.expand(e.target);
            }
        }, true);

        document.addEventListener('blur', (e) => {
            if (e.target.matches('.input-expandable')) {
                setTimeout(() => this.collapse(e.target), 150);
            }
        }, true);

        document.addEventListener('input', (e) => {
            if (e.target.matches('.input-expandable')) {
                this.updateCharCounter(e.target);
            }
        }, true);
    },

    setupKeyboardListeners() {
        document.addEventListener('keydown', (e) => {
            if (e.target.matches('.input-expandable')) {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.saveAndCollapse(e.target);
                } else if (e.key === 'Escape') {
                    e.preventDefault();
                    this.restoreAndCollapse(e.target);
                }
            }
        });
    },

    expand(input) {
        if (this.expandedInputs.has(input)) return;

        this.expandedInputs.add(input);
        input.dataset.originalValue = input.value;

        // 创建字符计数器
        if (!input.dataset.hasCounter) {
            const counter = document.createElement('div');
            counter.className = 'char-counter';
            counter.style.cssText = `
                position: absolute;
                bottom: -20px;
                right: 0;
                font-size: 11px;
                color: #6c757d;
                background: white;
                padding: 2px 6px;
                border-radius: 3px;
                opacity: 0;
                transition: opacity 0.2s ease;
                z-index: 101;
            `;
            input.parentNode.appendChild(counter);
            input.dataset.hasCounter = 'true';
            this.updateCharCounter(input);
        }

        // 特殊处理某些类型的输入框
        if (input.name === 'header_pattern') {
            input.style.fontFamily = 'Monaco, Menlo, "Ubuntu Mono", monospace';
            input.style.fontSize = '13px';
        }
    },

    collapse(input) {
        if (!this.expandedInputs.has(input)) return;

        this.expandedInputs.delete(input);

        // 隐藏字符计数器
        const counter = input.parentNode.querySelector('.char-counter');
        if (counter) {
            counter.style.opacity = '0';
        }

        // 重置样式
        if (input.name === 'header_pattern') {
            input.style.fontFamily = '';
            input.style.fontSize = '';
        }
    },

    updateCharCounter(input) {
        const counter = input.parentNode.querySelector('.char-counter');
        if (counter) {
            const length = input.value.length;
            counter.textContent = `${length} 字符`;
            counter.style.opacity = '1';
        }
    },

    saveAndCollapse(input) {
        const form = input.closest('form');
        if (form) {
            // 触发表单提交
            const submitEvent = new Event('submit', { cancelable: true });
            form.dispatchEvent(submitEvent);
        }
        this.collapse(input);
        input.blur();
    },

    restoreAndCollapse(input) {
        if (input.dataset.originalValue !== undefined) {
            input.value = input.dataset.originalValue;
        }
        this.collapse(input);
        input.blur();
    }
};

// 表单处理
const FormHandler = {
    init() {
        console.log('Form handler init...');
        const forms = document.querySelectorAll('form[method="get"]');
        forms.forEach(form => {
            form.addEventListener('submit', this.handleSubmit.bind(this));
        });
    },

    async handleSubmit(e) {
        e.preventDefault();

        const form = e.target;
        const submitBtn = form.querySelector('button[type="submit"]');

        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>保存中...';
        }

        try {
            const formData = new FormData(form);
            const params = new URLSearchParams(formData);
            const response = await fetch(`${form.action}?${params}`, {
                method: 'GET'
            });

            if (response.status === 302 || response.status === 0) {
                // 重定向表示成功
                SimpleToast.success('✅ 更新成功！');
                setTimeout(() => window.location.reload(), 3000);
            } else if (response.status === 403) {
                // 403错误 - 未锁定或被他人锁定
                try {
                    const data = await response.json();
                    SimpleToast.error(`❌ ${data.error || '请先锁定此Ingress再进行修改'}`);
                } catch {
                    SimpleToast.error('❌ 请先锁定此Ingress再进行修改');
                }
            } else if (response.ok) {
                // 其他成功状态
                SimpleToast.success('✅ 更新成功！');
                setTimeout(() => window.location.reload(), 3000);
            } else {
                // 其他错误
                const text = await response.text();
                SimpleToast.error(`❌ 更新失败 (${response.status}): ${text}`);
            }
        } catch (error) {
            console.error('提交错误:', error);
            SimpleToast.error('❌ 更新失败，请检查网络连接');
        } finally {
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.textContent = 'Update';
            }
        }
    }
};

// 表单验证
const FormValidator = {
    init() {
        console.log('Form validator init...');
        const forms = document.querySelectorAll('form[method="get"]');
        forms.forEach(form => {
            form.addEventListener('submit', this.validate.bind(this));
        });
    },

    validate(e) {
        const form = e.target;
        const errors = [];

        const headerValue = form.header_value.value.trim();
        const headerPattern = form.header_pattern.value.trim();
        const weight = parseInt(form.weight.value, 10);

        // 验证Header配置
        if (headerValue && headerPattern) {
            errors.push({
                field: 'header_value',
                message: 'canary-by-header-value 和 canary-by-header-pattern 不能同时设置'
            });
        }

        // 验证正则表达式
        if (headerPattern) {
            try {
                new RegExp(headerPattern);
            } catch(e) {
                errors.push({
                    field: 'header_pattern',
                    message: `正则格式错误: ${e.message}`
                });
            }
        }

        // 验证权重
        if (isNaN(weight) || weight < 0 || weight > 100) {
            errors.push({
                field: 'weight',
                message: 'canary-weight 必须是 0-100 的整数'
            });
        }

        // 显示错误
        this.showErrors(form, errors);

        if (errors.length > 0) {
            e.preventDefault();
            SimpleToast.error(errors[0].message);
        }
    },

    showErrors(form, errors) {
        // 清除之前的错误
        this.clearErrors(form);

        if (errors.length === 0) return;

        errors.forEach(error => {
            const field = form[error.field];
            if (field) {
                field.style.borderColor = '#dc3545';
                field.style.boxShadow = '0 0 0 3px rgba(220, 53, 69, 0.25)';

                // 创建错误提示
                const errorMsg = document.createElement('div');
                errorMsg.style.cssText = `
                    position: absolute;
                    bottom: -22px;
                    left: 0;
                    font-size: 12px;
                    color: #dc3545;
                    background: white;
                    padding: 2px 8px;
                    border-radius: 4px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    z-index: 102;
                    white-space: nowrap;
                    animation: fadeIn 0.2s ease-out;
                `;
                errorMsg.textContent = error.message;
                field.parentNode.appendChild(errorMsg);

                // 输入框获得焦点时清除错误
                field.addEventListener('focus', () => {
                    this.clearFieldError(field);
                }, { once: true });
            }
        });
    },

    clearErrors(form) {
        form.querySelectorAll('input').forEach(field => {
            this.clearFieldError(field);
        });
    },

    clearFieldError(field) {
        field.style.borderColor = '';
        field.style.boxShadow = '';
        const errorMsg = field.parentNode.querySelector('div[style*="color: #dc3545"]');
        if (errorMsg) {
            errorMsg.remove();
        }
    }
};

// 初始化所有功能
function initCanaryController() {
    console.log('Initializing Canary Controller...');

    // 初始化各个模块
    SimpleToast.init();
    InputExpander.init();
    FormHandler.init();
    FormValidator.init();

    // 给所有输入框添加可展开样式
    const inputs = document.querySelectorAll('input[type="text"], input[type="number"]');
    inputs.forEach(input => {
        input.classList.add('input-expandable');
        input.style.cssText += `
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            cursor: text;
        `;

        input.addEventListener('focus', function() {
            this.style.minWidth = '250px';
            this.style.maxWidth = '400px';
            this.style.boxShadow = '0 0 0 3px rgba(13, 110, 253, 0.25)';
            this.style.borderColor = '#0d6efd';
            this.style.transform = 'scale(1.02)';
        });

        input.addEventListener('blur', function() {
            this.style.minWidth = '';
            this.style.maxWidth = '';
            this.style.boxShadow = '';
            this.style.borderColor = '';
            this.style.transform = '';
        });
    });

    console.log('Canary Controller initialized successfully');
}

// 导出到全局
window.CanaryController = {
    Toast: SimpleToast,
    InputExpander: InputExpander,
    FormHandler: FormHandler,
    FormValidator: FormValidator
};

// 兼容旧的接口
window.CanaryInputEnhancer = {
    Toast: SimpleToast
};

// Lock/Unlock API服务
const LockService = {
    async lock(namespace, ingress) {
        try {
            const formData = new FormData();
            formData.append("namespace", namespace);
            formData.append("ingress", ingress);
            const resp = await fetch("/lock", {
                method: "POST",
                body: formData,
                credentials: "same-origin"
            });
            const data = await resp.json();

            if (!resp.ok) {
                SimpleToast.error(data.error || "Lock failed");
                return false;
            } else {
                SimpleToast.success("Lock successful!");
                setTimeout(() => location.reload(), 1000);
                return true;
            }
        } catch (error) {
            console.error('Lock error:', error);
            SimpleToast.error("Lock failed due to network error");
            return false;
        }
    },

    async unlock(namespace, ingress) {
        try {
            const formData = new FormData();
            formData.append("namespace", namespace);
            formData.append("ingress", ingress);
            const resp = await fetch("/unlock", {
                method: "POST",
                body: formData,
                credentials: "same-origin"
            });
            const data = await resp.json();

            if (!resp.ok) {
                SimpleToast.error(data.error || "Unlock failed");
                return false;
            } else {
                SimpleToast.success("Unlock successful!");
                setTimeout(() => location.reload(), 1000);
                return true;
            }
        } catch (error) {
            console.error('Unlock error:', error);
            SimpleToast.error("Unlock failed due to network error");
            return false;
        }
    }
};

// 导出到全局（兼容旧的调用方式）
window.lockIngress = (ns, ing) => LockService.lock(ns, ing);
window.unlockIngress = (ns, ing) => LockService.unlock(ns, ing);

// 开发环境下的测试函数
if (window.location.hostname === '127.0.0.1' || window.location.hostname === 'localhost') {
    window.testToast = function(type) {
        console.log('Testing toast:', type);
        if (window.CanaryController && window.CanaryController.Toast) {
            switch(type) {
                case 'success':
                    window.CanaryController.Toast.success('✅ 成功提示测试');
                    break;
                case 'error':
                    window.CanaryController.Toast.error('❌ 错误提示测试');
                    break;
                case 'warning':
                    window.CanaryController.Toast.warning('⚠️ 警告提示测试');
                    break;
            }
        }
    };
}

console.log('Canary Main JavaScript loaded successfully');

// 页面加载完成后初始化
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initCanaryController);
} else {
    initCanaryController();
}