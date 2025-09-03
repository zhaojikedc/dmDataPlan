/**
 * 数据API交互库
 * 用于HTML页面与JSON数据的动态交互
 */

class DataAPI {
    constructor(baseUrl = 'http://localhost:8080') {
        this.baseUrl = baseUrl;
    }

    /**
     * 发送HTTP请求
     * @param {string} method - HTTP方法
     * @param {string} url - 请求URL
     * @param {Object} data - 请求数据
     * @returns {Promise} 响应数据
     */
    async request(method, url, data = null) {
        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        };

        if (data && (method === 'POST' || method === 'PUT')) {
            options.body = JSON.stringify(data);
        }

        try {
            const response = await fetch(url, options);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('API请求失败:', error);
            throw error;
        }
    }

    /**
     * 获取数据
     * @param {string} filename - JSON文件名
     * @param {string} itemType - 项目类型（可选）
     * @returns {Promise<Object>} 数据对象
     */
    async getData(filename, itemType = null) {
        const params = new URLSearchParams({ file: filename });
        if (itemType) {
            params.append('type', itemType);
        }
        
        const url = `${this.baseUrl}/api/data?${params}`;
        return await this.request('GET', url);
    }

    /**
     * 获取特定项目
     * @param {string} filename - JSON文件名
     * @param {string} itemType - 项目类型
     * @param {string} itemId - 项目ID
     * @returns {Promise<Object>} 项目数据
     */
    async getItem(filename, itemType, itemId) {
        const url = `${this.baseUrl}/api/data/${filename}/${itemType}/${itemId}`;
        return await this.request('GET', url);
    }

    /**
     * 添加项目
     * @param {string} filename - JSON文件名
     * @param {string} itemType - 项目类型
     * @param {Object} itemData - 项目数据
     * @returns {Promise<boolean>} 是否成功
     */
    async addItem(filename, itemType, itemData) {
        const data = {
            filename: filename,
            type: itemType,
            data: itemData
        };
        
        const url = `${this.baseUrl}/api/data`;
        const result = await this.request('POST', url, data);
        return result.success || false;
    }

    /**
     * 更新项目
     * @param {string} filename - JSON文件名
     * @param {string} itemType - 项目类型
     * @param {string} itemId - 项目ID
     * @param {Object} updateData - 更新数据
     * @returns {Promise<boolean>} 是否成功
     */
    async updateItem(filename, itemType, itemId, updateData) {
        const url = `${this.baseUrl}/api/data/${filename}/${itemType}/${itemId}`;
        const result = await this.request('POST', url, updateData);
        return result.success || false;
    }

    /**
     * 删除项目
     * @param {string} filename - JSON文件名
     * @param {string} itemType - 项目类型
     * @param {string} itemId - 项目ID
     * @returns {Promise<boolean>} 是否成功
     */
    async deleteItem(filename, itemType, itemId) {
        const url = `${this.baseUrl}/api/data/${filename}/${itemType}/${itemId}`;
        const result = await this.request('DELETE', url);
        return result.success || false;
    }

    /**
     * 获取文件统计信息
     * @param {string} filename - JSON文件名
     * @returns {Promise<Object>} 统计信息
     */
    async getStats(filename) {
        const url = `${this.baseUrl}/api/stats?file=${filename}`;
        return await this.request('GET', url);
    }

    /**
     * 列出指定类型的所有项目
     * @param {string} filename - JSON文件名
     * @param {string} itemType - 项目类型
     * @returns {Promise<Array>} 项目列表
     */
    async listItems(filename, itemType) {
        const data = await this.getData(filename, itemType);
        return Array.isArray(data) ? data : [];
    }

    /**
     * 搜索项目
     * @param {string} filename - JSON文件名
     * @param {string} itemType - 项目类型
     * @param {string} searchKey - 搜索字段
     * @param {string} searchValue - 搜索值
     * @returns {Promise<Array>} 匹配的项目列表
     */
    async searchItems(filename, itemType, searchKey, searchValue) {
        const items = await this.listItems(filename, itemType);
        return items.filter(item => 
            String(item[searchKey] || '').toLowerCase().includes(searchValue.toLowerCase())
        );
    }
}

/**
 * 数据表格管理器
 */
class DataTableManager {
    constructor(api, tableId, filename, itemType) {
        this.api = api;
        this.tableId = tableId;
        this.filename = filename;
        this.itemType = itemType;
        this.data = [];
        this.currentPage = 1;
        this.pageSize = 10;
    }

    /**
     * 初始化表格
     */
    async init() {
        await this.loadData();
        this.renderTable();
        this.bindEvents();
    }

    /**
     * 加载数据
     */
    async loadData() {
        try {
            this.data = await this.api.listItems(this.filename, this.itemType);
            console.log(`加载了 ${this.data.length} 条数据`);
        } catch (error) {
            console.error('加载数据失败:', error);
            this.data = [];
        }
    }

    /**
     * 渲染表格
     */
    renderTable() {
        const table = document.getElementById(this.tableId);
        if (!table) {
            console.error(`表格元素不存在: ${this.tableId}`);
            return;
        }

        const tbody = table.querySelector('tbody');
        if (!tbody) {
            console.error('表格tbody元素不存在');
            return;
        }

        // 清空现有内容
        tbody.innerHTML = '';

        // 计算分页
        const startIndex = (this.currentPage - 1) * this.pageSize;
        const endIndex = startIndex + this.pageSize;
        const pageData = this.data.slice(startIndex, endIndex);

        // 渲染数据行
        pageData.forEach((item, index) => {
            const row = this.createTableRow(item, startIndex + index);
            tbody.appendChild(row);
        });

        // 更新分页信息
        this.updatePagination();
    }

    /**
     * 创建表格行
     * @param {Object} item - 数据项
     * @param {number} index - 索引
     * @returns {HTMLElement} 表格行元素
     */
    createTableRow(item, index) {
        const row = document.createElement('tr');
        
        // 根据数据类型创建不同的列
        Object.keys(item).forEach(key => {
            if (key !== 'id' && key !== 'created_at' && key !== 'updated_at') {
                const cell = document.createElement('td');
                cell.textContent = item[key] || '';
                row.appendChild(cell);
            }
        });

        // 添加操作列
        const actionCell = document.createElement('td');
        
        // 创建编辑按钮
        const editBtn = document.createElement('button');
        editBtn.className = 'btn-edit';
        editBtn.setAttribute('data-id', item.id);
        editBtn.textContent = '编辑';
        
        // 创建删除按钮
        const deleteBtn = document.createElement('button');
        deleteBtn.className = 'btn-delete';
        deleteBtn.setAttribute('data-id', item.id);
        deleteBtn.textContent = '删除';
        
        actionCell.appendChild(editBtn);
        actionCell.appendChild(deleteBtn);
        row.appendChild(actionCell);

        return row;
    }

    /**
     * 更新分页信息
     */
    updatePagination() {
        const totalPages = Math.ceil(this.data.length / this.pageSize);
        const paginationInfo = document.getElementById(`${this.tableId}-pagination`);
        
        if (paginationInfo) {
            paginationInfo.innerHTML = `
                <span>第 ${this.currentPage} 页，共 ${totalPages} 页</span>
                <span>总计 ${this.data.length} 条记录</span>
                <button ${this.currentPage <= 1 ? 'disabled' : ''} onclick="dataTable.prevPage()">上一页</button>
                <button ${this.currentPage >= totalPages ? 'disabled' : ''} onclick="dataTable.nextPage()">下一页</button>
            `;
        }
    }

    /**
     * 绑定事件
     */
    bindEvents() {
        const table = document.getElementById(this.tableId);
        if (!table) return;

        // 删除按钮事件
        table.addEventListener('click', async (e) => {
            if (e.target.classList.contains('btn-delete')) {
                const itemId = e.target.getAttribute('data-id');
                if (confirm('确定要删除这条记录吗？')) {
                    await this.deleteItem(itemId);
                }
            }
        });

        // 编辑按钮事件
        table.addEventListener('click', (e) => {
            if (e.target.classList.contains('btn-edit')) {
                const itemId = e.target.getAttribute('data-id');
                this.editItem(itemId);
            }
        });
    }

    /**
     * 删除项目
     * @param {string} itemId - 项目ID
     */
    async deleteItem(itemId) {
        try {
            const success = await this.api.deleteItem(this.filename, this.itemType, itemId);
            if (success) {
                alert('删除成功');
                await this.loadData();
                this.renderTable();
            } else {
                alert('删除失败');
            }
        } catch (error) {
            console.error('删除失败:', error);
            alert('删除失败: ' + error.message);
        }
    }

    /**
     * 编辑项目
     * @param {string} itemId - 项目ID
     */
    editItem(itemId) {
        const item = this.data.find(item => item.id === itemId);
        if (item) {
            // 这里可以实现编辑功能
            console.log('编辑项目:', item);
            alert('编辑功能待实现');
        }
    }

    /**
     * 上一页
     */
    prevPage() {
        if (this.currentPage > 1) {
            this.currentPage--;
            this.renderTable();
        }
    }

    /**
     * 下一页
     */
    nextPage() {
        const totalPages = Math.ceil(this.data.length / this.pageSize);
        if (this.currentPage < totalPages) {
            this.currentPage++;
            this.renderTable();
        }
    }

    /**
     * 刷新数据
     */
    async refresh() {
        await this.loadData();
        this.renderTable();
    }
}

// 全局API实例
const dataAPI = new DataAPI();

// 全局数据表格实例
let dataTable = null;

/**
 * 初始化数据表格
 * @param {string} tableId - 表格ID
 * @param {string} filename - JSON文件名
 * @param {string} itemType - 项目类型
 */
function initDataTable(tableId, filename, itemType) {
    dataTable = new DataTableManager(dataAPI, tableId, filename, itemType);
    dataTable.init();
}

/**
 * 显示加载状态
 * @param {string} elementId - 元素ID
 */
function showLoading(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = '<div class="loading">加载中...</div>';
    }
}

/**
 * 隐藏加载状态
 * @param {string} elementId - 元素ID
 */
function hideLoading(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        const loading = element.querySelector('.loading');
        if (loading) {
            loading.remove();
        }
    }
}

/**
 * 显示错误信息
 * @param {string} message - 错误信息
 */
function showError(message) {
    alert('错误: ' + message);
}

/**
 * 显示成功信息
 * @param {string} message - 成功信息
 */
function showSuccess(message) {
    alert('成功: ' + message);
}
