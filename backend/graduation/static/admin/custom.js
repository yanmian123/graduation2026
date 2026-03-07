/*
 * 自定义Django Admin JavaScript
 * 增强管理员界面功能（绿色系）
 */

document.addEventListener('DOMContentLoaded', function() {
    // 添加欢迎消息
    addWelcomeMessage();
    
    // 添加快速操作按钮
    addQuickActions();
    
    // 添加统计信息
    addDashboardStats();
    
    // 优化表格显示
    optimizeTableDisplay();
    
    // 添加搜索增强功能
    enhanceSearch();
    
    // 添加批量操作
    addBatchActions();
});

/**
 * 添加欢迎消息
 */
function addWelcomeMessage() {
    const header = document.querySelector('#header');
    if (header) {
        const welcomeDiv = document.createElement('div');
        welcomeDiv.style.cssText = `
            background: rgb(95, 133, 127);
            color: white;
            padding: 10px 20px;
            margin: 0 0 20px 0;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(95, 133, 127, 0.15);
            font-size: 14px;
        `;
        welcomeDiv.innerHTML = `
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 20px;">👋</span>
                <span>欢迎来到大学生就业信息共享平台管理后台</span>
            </div>
        `;
        header.insertAdjacentElement('afterend', welcomeDiv);
    }
}

/**
 * 添加快速操作按钮
 */
function addQuickActions() {
    const dashboard = document.querySelector('.dashboard');
    if (dashboard) {
        const quickActionsDiv = document.createElement('div');
        quickActionsDiv.style.cssText = `
            background: white;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        `;
        quickActionsDiv.innerHTML = `
            <h3 style="margin: 0 0 15px 0; color: rgb(95, 133, 127); font-size: 18px;">快速操作</h3>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
                <a href="/admin/register/user/" style="
                    display: flex;
                    align-items: center;
                    gap: 10px;
                    padding: 15px;
                    background: rgb(95, 133, 127);
                    color: white;
                    text-decoration: none;
                    border-radius: 6px;
                    transition: all 0.3s ease;
                    box-shadow: 0 2px 6px rgba(95, 133, 127, 0.2);
                " onmouseover="this.style.transform='translateY(-2px)'" onmouseout="this.style.transform='translateY(0)'">
                    <span style="font-size: 24px;">👥</span>
                    <div>
                        <div style="font-weight: 600; font-size: 16px;">用户管理</div>
                        <div style="font-size: 12px; opacity: 0.9;">管理平台用户</div>
                    </div>
                </a>
                <a href="/admin/enterprise/enterprise/" style="
                    display: flex;
                    align-items: center;
                    gap: 10px;
                    padding: 15px;
                    background: rgb(95, 133, 127);
                    color: white;
                    text-decoration: none;
                    border-radius: 6px;
                    transition: all 0.3s ease;
                    box-shadow: 0 2px 6px rgba(95, 133, 127, 0.2);
                " onmouseover="this.style.transform='translateY(-2px)'" onmouseout="this.style.transform='translateY(0)'">
                    <span style="font-size: 24px;">🏢</span>
                    <div>
                        <div style="font-weight: 600; font-size: 16px;">企业管理</div>
                        <div style="font-size: 12px; opacity: 0.9;">审核企业信息</div>
                    </div>
                </a>
                <a href="/admin/article_publish/article/" style="
                    display: flex;
                    align-items: center;
                    gap: 10px;
                    padding: 15px;
                    background: rgb(95, 133, 127);
                    color: white;
                    text-decoration: none;
                    border-radius: 6px;
                    transition: all 0.3s ease;
                    box-shadow: 0 2px 6px rgba(95, 133, 127, 0.2);
                " onmouseover="this.style.transform='translateY(-2px)'" onmouseout="this.style.transform='translateY(0)'">
                    <span style="font-size: 24px;">📝</span>
                    <div>
                        <div style="font-weight: 600; font-size: 16px;">文章管理</div>
                        <div style="font-size: 12px; opacity: 0.9;">管理平台文章</div>
                    </div>
                </a>
                <a href="/admin/notification/announcement/" style="
                    display: flex;
                    align-items: center;
                    gap: 10px;
                    padding: 15px;
                    background: rgb(95, 133, 127);
                    color: white;
                    text-decoration: none;
                    border-radius: 6px;
                    transition: all 0.3s ease;
                    box-shadow: 0 2px 6px rgba(95, 133, 127, 0.2);
                " onmouseover="this.style.transform='translateY(-2px)'" onmouseout="this.style.transform='translateY(0)'">
                    <span style="font-size: 24px;">📢</span>
                    <div>
                        <div style="font-weight: 600; font-size: 16px;">公告管理</div>
                        <div style="font-size: 12px; opacity: 0.9;">发布系统公告</div>
                    </div>
                </a>
            </div>
        `;
        dashboard.insertAdjacentElement('afterbegin', quickActionsDiv);
    }
}

/**
 * 添加统计信息
 */
function addDashboardStats() {
    const dashboard = document.querySelector('.dashboard');
    if (dashboard) {
        const statsDiv = document.createElement('div');
        statsDiv.style.cssText = `
            background: white;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        `;
        statsDiv.innerHTML = `
            <h3 style="margin: 0 0 15px 0; color: rgb(95, 133, 127); font-size: 18px;">平台统计</h3>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px;">
                <div style="
                    padding: 15px;
                    background: rgb(95, 133, 127);
                    color: white;
                    border-radius: 6px;
                    text-align: center;
                ">
                    <div style="font-size: 24px; font-weight: 600; margin-bottom: 5px;">👥</div>
                    <div style="font-size: 14px;">用户总数</div>
                </div>
                <div style="
                    padding: 15px;
                    background: rgb(95, 133, 127);
                    color: white;
                    border-radius: 6px;
                    text-align: center;
                ">
                    <div style="font-size: 24px; font-weight: 600; margin-bottom: 5px;">🏢</div>
                    <div style="font-size: 14px;">企业总数</div>
                </div>
                <div style="
                    padding: 15px;
                    background: rgb(95, 133, 127);
                    color: white;
                    border-radius: 6px;
                    text-align: center;
                ">
                    <div style="font-size: 24px; font-weight: 600; margin-bottom: 5px;">📝</div>
                    <div style="font-size: 14px;">文章总数</div>
                </div>
                <div style="
                    padding: 15px;
                    background: rgb(95, 133, 127);
                    color: white;
                    border-radius: 6px;
                    text-align: center;
                ">
                    <div style="font-size: 24px; font-weight: 600; margin-bottom: 5px;">💼</div>
                    <div style="font-size: 14px;">职位总数</div>
                </div>
            </div>
        `;
        dashboard.insertAdjacentElement('afterbegin', statsDiv);
    }
}

/**
 * 优化表格显示
 */
function optimizeTableDisplay() {
    const table = document.querySelector('#result_list');
    if (table) {
        // 添加行高亮效果
        const rows = table.querySelectorAll('tbody tr');
        rows.forEach(row => {
            row.addEventListener('mouseenter', function() {
                this.style.backgroundColor = 'rgba(95, 133, 127, 0.1)';
            });
            row.addEventListener('mouseleave', function() {
                this.style.backgroundColor = '';
            });
        });
        
        // 添加操作按钮样式
        const actionLinks = table.querySelectorAll('a');
        actionLinks.forEach(link => {
            if (link.textContent.includes('删除')) {
                link.style.cssText = `
                    background: #ef4444;
                    color: white;
                    padding: 5px 15px;
                    border-radius: 4px;
                    text-decoration: none;
                    transition: all 0.3s ease;
                `;
                link.addEventListener('mouseenter', function() {
                    this.style.transform = 'translateY(-2px)';
                    this.style.boxShadow = '0 4px 12px rgba(239, 68, 68, 0.3)';
                });
                link.addEventListener('mouseleave', function() {
                    this.style.transform = 'translateY(0)';
                    this.style.boxShadow = '0 2px 6px rgba(239, 68, 68, 0.2)';
                });
            } else if (link.textContent.includes('编辑') || link.textContent.includes('修改')) {
                link.style.cssText = `
                    background: rgb(95, 133, 127);
                    color: white;
                    padding: 5px 15px;
                    border-radius: 4px;
                    text-decoration: none;
                    transition: all 0.3s ease;
                `;
                link.addEventListener('mouseenter', function() {
                    this.style.transform = 'translateY(-2px)';
                    this.style.boxShadow = '0 4px 12px rgba(95, 133, 127, 0.3)';
                });
                link.addEventListener('mouseleave', function() {
                    this.style.transform = 'translateY(0)';
                    this.style.boxShadow = '0 2px 6px rgba(95, 133, 127, 0.2)';
                });
            }
        });
    }
}

/**
 * 增强搜索功能
 */
function enhanceSearch() {
    const searchInput = document.querySelector('#searchbar');
    if (searchInput) {
        searchInput.style.cssText = `
            width: 100%;
            max-width: 400px;
            padding: 12px 20px;
            border: 2px solid rgb(95, 133, 127);
            border-radius: 25px;
            font-size: 14px;
            transition: all 0.3s ease;
            box-shadow: 0 2px 8px rgba(95, 133, 127, 0.1);
        `;
        searchInput.addEventListener('focus', function() {
            this.style.boxShadow = '0 4px 12px rgba(95, 133, 127, 0.2)';
            this.style.borderColor = 'rgb(95, 133, 127)';
        });
        searchInput.addEventListener('blur', function() {
            this.style.boxShadow = '0 2px 8px rgba(95, 133, 127, 0.1)';
            this.style.borderColor = 'rgb(95, 133, 127)';
        });
    }
}

/**
 * 添加批量操作
 */
function addBatchActions() {
    const changelist = document.querySelector('#changelist');
    if (changelist) {
        const batchActionsDiv = document.createElement('div');
        batchActionsDiv.style.cssText = `
            background: white;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 20px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            display: flex;
            gap: 10px;
            align-items: center;
        `;
        batchActionsDiv.innerHTML = `
            <span style="color: rgb(95, 133, 127); font-weight: 600;">批量操作：</span>
            <button onclick="batchApprove()" style="
                background: rgb(95, 133, 127);
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                cursor: pointer;
                transition: all 0.3s ease;
                font-weight: 600;
            ">批量审核通过</button>
            <button onclick="batchReject()" style="
                background: #ef4444;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                cursor: pointer;
                transition: all 0.3s ease;
                font-weight: 600;
            ">批量拒绝</button>
            <button onclick="exportData()" style="
                background: rgb(95, 133, 127);
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                cursor: pointer;
                transition: all 0.3s ease;
                font-weight: 600;
            ">导出数据</button>
        `;
        changelist.insertAdjacentElement('afterbegin', batchActionsDiv);
    }
}

// 批量审核通过
function batchApprove() {
    alert('批量审核通过功能（示例）');
}

// 批量拒绝
function batchReject() {
    alert('批量拒绝功能（示例）');
}

// 导出数据
function exportData() {
    alert('导出数据功能（示例）');
}