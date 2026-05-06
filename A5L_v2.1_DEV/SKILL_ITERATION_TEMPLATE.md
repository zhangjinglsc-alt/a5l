# SKILL标准模板

每个SKILL都应该包含以下部分：

## 1. SKILL元数据
```json
{
  "id": "skill_xxx",
  "name": "SKILL名称",
  "version": "1.0.0",
  "category": "trading|analysis|system|monitoring|reporting|ai|communication",
  "description": "SKILL功能描述",
  "author": "Evolution Daemon",
  "created_at": "2026-05-01T00:00:00+08:00",
  "updated_at": "2026-05-01T00:00:00+08:00",
  "enabled": true,
  "dependencies": [],
  "config": {}
}
```

## 2. SKILL标准接口
```python
class SkillBase:
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
    
    def initialize(self) -> bool:
        """初始化SKILL"""
        pass
    
    def execute(self, data: Dict) -> Dict:
        """执行SKILL核心功能"""
        pass
    
    def validate(self, data: Dict) -> bool:
        """验证输入数据"""
        pass
    
    def get_metadata(self) -> Dict:
        """获取SKILL元数据"""
        pass
    
    def get_status(self) -> Dict:
        """获取SKILL运行状态"""
        pass
    
    def cleanup(self) -> bool:
        """清理SKILL资源"""
        pass
```

## 3. SKILL标准文档
每个SKILL都应该包含：
- 功能说明
- 使用方法
- 配置参数
- 输入输出格式
- 依赖关系
- 示例代码

## 4. SKILL标准测试
每个SKILL都应该包含：
- 单元测试
- 集成测试
- 性能测试
- 错误处理测试
