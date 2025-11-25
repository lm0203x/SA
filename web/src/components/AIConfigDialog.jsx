import React, { useState, useEffect } from 'react';
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogHeader,
    DialogTitle,
} from '@/components/ui/dialog';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Brain, CheckCircle, XCircle, Loader2, Plus, Trash2, Edit, Star } from 'lucide-react';
import {
    getAIConfigs,
    createAIConfig,
    updateAIConfig,
    deleteAIConfig,
    testAIConfigConnection,
    setDefaultAIConfig,
    getAIConfigTypes
} from '@/services/api';

export default function AIConfigDialog({ open, onClose }) {
    const [aiConfigs, setAIConfigs] = useState([]);
    const [configTypes, setConfigTypes] = useState([]);
    const [loading, setLoading] = useState(true);
    const [testingId, setTestingId] = useState(null);
    const [editingId, setEditingId] = useState(null);
    const [message, setMessage] = useState({ type: '', text: '' });
    const [showCreateForm, setShowCreateForm] = useState(false);

    // 新建配置表单
    const [newConfigForm, setNewConfigForm] = useState({
        provider_type: 'tongyi',
        provider_name: '',
        config_data: {},
        is_active: false,
        is_default: false
    });

    // 编辑配置表单
    const [editForm, setEditForm] = useState({
        provider_name: '',
        config_data: {},
        is_active: false,
        is_default: false
    });

    // 加载数据
    useEffect(() => {
        if (open) {
            loadAIConfigs();
            loadConfigTypes();
        }
    }, [open]);

    const loadAIConfigs = async () => {
        try {
            setLoading(true);
            const response = await getAIConfigs();
            setAIConfigs(response.data || []);
            setMessage({ type: '', text: '' });
        } catch (error) {
            console.error('加载AI配置失败:', error);
            setMessage({ type: 'error', text: `加载失败: ${error.message}` });
        } finally {
            setLoading(false);
        }
    };

    const loadConfigTypes = async () => {
        try {
            const response = await getAIConfigTypes();
            setConfigTypes(response.data || []);
        } catch (error) {
            console.error('加载配置类型失败:', error);
        }
    };

    // 测试连接
    const handleTestConnection = async (id) => {
        try {
            setTestingId(id);
            setMessage({ type: '', text: '' });

            const response = await testAIConfigConnection(id);

            if (response.success) {
                setMessage({ type: 'success', text: '✅ AI服务连接测试成功！' });
                loadAIConfigs();
            } else {
                setMessage({ type: 'error', text: `❌ 连接测试失败: ${response.message}` });
            }
        } catch (error) {
            console.error('测试连接失败:', error);
            setMessage({ type: 'error', text: `❌ 测试失败: ${error.message}` });
        } finally {
            setTestingId(null);
        }
    };

    // 设置默认配置
    const handleSetDefault = async (id) => {
        try {
            setMessage({ type: '', text: '' });
            const response = await setDefaultAIConfig(id);

            if (response.success) {
                setMessage({ type: 'success', text: '✅ 已设置为默认AI服务' });
                loadAIConfigs();
            }
        } catch (error) {
            console.error('设置默认配置失败:', error);
            setMessage({ type: 'error', text: `❌ 设置失败: ${error.message}` });
        }
    };

    // 切换激活状态
    const handleToggleActive = async (config) => {
        try {
            setMessage({ type: '', text: '' });

            await updateAIConfig(config.id, {
                is_active: !config.is_active
            });

            setMessage({
                type: 'success',
                text: `✅ AI服务已${!config.is_active ? '激活' : '停用'}`
            });
            loadAIConfigs();
        } catch (error) {
            console.error('更新AI配置失败:', error);
            setMessage({ type: 'error', text: `❌ 更新失败: ${error.message}` });
        }
    };

    // 创建新配置
    const handleCreateConfig = async () => {
        if (!newConfigForm.provider_name.trim()) {
            setMessage({ type: 'error', text: '请输入配置名称' });
            return;
        }

        // 验证必需字段
        const selectedType = configTypes.find(t => t.type === newConfigForm.provider_type);
        if (selectedType) {
            for (const field of selectedType.required_fields) {
                if (!newConfigForm.config_data[field]) {
                    setMessage({ type: 'error', text: `请填写必需字段: ${field}` });
                    return;
                }
            }
        }

        try {
            setMessage({ type: '', text: '' });
            const response = await createAIConfig(newConfigForm);

            if (response.success) {
                setMessage({ type: 'success', text: '✅ AI配置创建成功' });
                setShowCreateForm(false);
                setNewConfigForm({
                    provider_type: 'tongyi',
                    provider_name: '',
                    config_data: {},
                    is_active: false,
                    is_default: false
                });
                loadAIConfigs();
            }
        } catch (error) {
            console.error('创建AI配置失败:', error);
            setMessage({ type: 'error', text: `❌ 创建失败: ${error.message}` });
        }
    };

    // 更新配置
    const handleUpdateConfig = async (config) => {
        try {
            setMessage({ type: '', text: '' });

            await updateAIConfig(config.id, editForm);

            setMessage({ type: 'success', text: '✅ 配置更新成功' });
            setEditingId(null);
            setEditForm({
                provider_name: '',
                config_data: {},
                is_active: false,
                is_default: false
            });
            loadAIConfigs();
        } catch (error) {
            console.error('更新配置失败:', error);
            setMessage({ type: 'error', text: `❌ 更新失败: ${error.message}` });
        }
    };

    // 删除配置
    const handleDelete = async (id) => {
        if (!confirm('确定要删除此AI配置吗？')) return;

        try {
            setMessage({ type: '', text: '' });
            await deleteAIConfig(id);
            setMessage({ type: 'success', text: '✅ AI配置已删除' });
            loadAIConfigs();
        } catch (error) {
            console.error('删除AI配置失败:', error);
            setMessage({ type: 'error', text: `❌ 删除失败: ${error.message}` });
        }
    };

    // 获取配置类型信息
    const getTypeInfo = (providerType) => {
        return configTypes.find(t => t.type === providerType) || {};
    };

    // 渲染状态徽章
    const renderStatusBadge = (config) => {
        if (config.is_active && config.is_default) {
            return <Badge className="bg-green-500"><Star className="h-3 w-3 mr-1" />默认激活</Badge>;
        }
        if (config.is_active) {
            return <Badge className="bg-green-500">已激活</Badge>;
        }
        if (config.status === '成功') {
            return <Badge className="bg-blue-500">已测试</Badge>;
        }
        return <Badge variant="outline">未测试</Badge>;
    };

    // 渲染配置字段
    const renderConfigFields = (providerType, configData, onChange) => {
        const typeInfo = getTypeInfo(providerType);
        if (!typeInfo.required_fields) return null;

        const allFields = [...typeInfo.required_fields, ...(typeInfo.optional_fields || [])];

        return allFields.map(field => {
            const isRequired = typeInfo.required_fields.includes(field);
            const defaultValue = typeInfo.default_config?.[field] || '';

            return (
                <div key={field}>
                    <Label htmlFor={`field-${field}`}>
                        {field} {isRequired && <span className="text-red-500">*</span>}
                    </Label>
                    <Input
                        id={`field-${field}`}
                        type={field.includes('key') ? 'password' : 'text'}
                        placeholder={defaultValue ? `默认: ${defaultValue}` : ''}
                        value={configData[field] || ''}
                        onChange={(e) => onChange(field, e.target.value)}
                        className="mt-1"
                    />
                </div>
            );
        });
    };

    return (
        <Dialog open={open} onOpenChange={onClose}>
            <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
                <DialogHeader>
                    <DialogTitle className="flex items-center gap-2">
                        <Brain className="h-5 w-5" />
                        AI服务配置
                    </DialogTitle>
                    <DialogDescription>
                        配置AI服务提供商，支持通义千问、OpenAI、Ollama等多种AI服务
                    </DialogDescription>
                </DialogHeader>

                <div className="space-y-4">
                    {/* 消息提示 */}
                    {message.text && (
                        <Alert className={message.type === 'error' ? 'border-red-500' : 'border-green-500'}>
                            <AlertDescription>{message.text}</AlertDescription>
                        </Alert>
                    )}

                    {/* 添加配置按钮 */}
                    <div className="flex justify-end">
                        <Button onClick={() => setShowCreateForm(!showCreateForm)} size="sm">
                            <Plus className="h-4 w-4 mr-1" />
                            添加配置
                        </Button>
                    </div>

                    {/* 创建配置表单 */}
                    {showCreateForm && (
                        <Card className="border-2 border-blue-200">
                            <CardHeader>
                                <CardTitle className="text-lg">新建AI配置</CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <Label htmlFor="provider-type">AI服务类型 *</Label>
                                        <Select
                                            value={newConfigForm.provider_type}
                                            onValueChange={(value) => {
                                                setNewConfigForm({
                                                    ...newConfigForm,
                                                    provider_type: value,
                                                    config_data: {}
                                                });
                                            }}
                                        >
                                            <SelectTrigger>
                                                <SelectValue />
                                            </SelectTrigger>
                                            <SelectContent>
                                                {configTypes.map(type => (
                                                    <SelectItem key={type.type} value={type.type}>
                                                        {type.name}
                                                    </SelectItem>
                                                ))}
                                            </SelectContent>
                                        </Select>
                                    </div>

                                    <div>
                                        <Label htmlFor="provider-name">配置名称 *</Label>
                                        <Input
                                            id="provider-name"
                                            placeholder="例如：通义千问-生产环境"
                                            value={newConfigForm.provider_name}
                                            onChange={(e) => setNewConfigForm({
                                                ...newConfigForm,
                                                provider_name: e.target.value
                                            })}
                                        />
                                    </div>
                                </div>

                                <div className="grid grid-cols-2 gap-4">
                                    {renderConfigFields(
                                        newConfigForm.provider_type,
                                        newConfigForm.config_data,
                                        (field, value) => {
                                            setNewConfigForm({
                                                ...newConfigForm,
                                                config_data: {
                                                    ...newConfigForm.config_data,
                                                    [field]: value
                                                }
                                            });
                                        }
                                    )}
                                </div>

                                <div className="flex gap-2">
                                    <Button onClick={handleCreateConfig} size="sm">
                                        <CheckCircle className="h-4 w-4 mr-1" />
                                        创建
                                    </Button>
                                    <Button
                                        onClick={() => {
                                            setShowCreateForm(false);
                                            setNewConfigForm({
                                                provider_type: 'tongyi',
                                                provider_name: '',
                                                config_data: {},
                                                is_active: false,
                                                is_default: false
                                            });
                                        }}
                                        variant="outline"
                                        size="sm"
                                    >
                                        取消
                                    </Button>
                                </div>
                            </CardContent>
                        </Card>
                    )}

                    {/* AI配置列表 */}
                    {loading ? (
                        <div className="flex justify-center items-center py-8">
                            <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
                            <span className="ml-2 text-gray-500">加载中...</span>
                        </div>
                    ) : aiConfigs.length === 0 ? (
                        <Card>
                            <CardContent className="text-center py-8">
                                <Brain className="h-12 w-12 mx-auto text-gray-400 mb-4" />
                                <p className="text-gray-600">暂无AI配置</p>
                                <p className="text-sm text-gray-500 mt-2">点击"添加配置"创建第一个AI服务配置</p>
                            </CardContent>
                        </Card>
                    ) : (
                        <div className="space-y-3">
                            {aiConfigs.map((config) => (
                                <Card key={config.id} className="border">
                                    <CardHeader className="pb-3">
                                        <div className="flex items-center justify-between">
                                            <div className="flex items-center gap-3">
                                                <Brain className="h-5 w-5 text-purple-500" />
                                                <div>
                                                    <CardTitle className="text-base">{config.provider_name}</CardTitle>
                                                    <CardDescription className="text-xs">
                                                        {getTypeInfo(config.provider_type).name || config.provider_type}
                                                    </CardDescription>
                                                </div>
                                            </div>
                                            {renderStatusBadge(config)}
                                        </div>
                                    </CardHeader>
                                    <CardContent className="space-y-3">
                                        {/* 编辑表单 */}
                                        {editingId === config.id ? (
                                            <div className="space-y-3 p-3 bg-gray-50 rounded-lg">
                                                <div>
                                                    <Label className="text-sm">配置名称</Label>
                                                    <Input
                                                        value={editForm.provider_name}
                                                        onChange={(e) => setEditForm({
                                                            ...editForm,
                                                            provider_name: e.target.value
                                                        })}
                                                        className="mt-1"
                                                        size="sm"
                                                    />
                                                </div>
                                                <div className="grid grid-cols-2 gap-3">
                                                    {renderConfigFields(
                                                        config.provider_type,
                                                        editForm.config_data,
                                                        (field, value) => {
                                                            setEditForm({
                                                                ...editForm,
                                                                config_data: {
                                                                    ...editForm.config_data,
                                                                    [field]: value
                                                                }
                                                            });
                                                        }
                                                    )}
                                                </div>
                                                <div className="flex gap-2">
                                                    <Button
                                                        onClick={() => handleUpdateConfig(config)}
                                                        size="sm"
                                                    >
                                                        <CheckCircle className="h-3 w-3 mr-1" />
                                                        保存
                                                    </Button>
                                                    <Button
                                                        onClick={() => {
                                                            setEditingId(null);
                                                            setEditForm({
                                                                provider_name: '',
                                                                config_data: {},
                                                                is_active: false,
                                                                is_default: false
                                                            });
                                                        }}
                                                        variant="outline"
                                                        size="sm"
                                                    >
                                                        取消
                                                    </Button>
                                                </div>
                                            </div>
                                        ) : (
                                            <div className="flex flex-wrap items-center gap-2">
                                                <Button
                                                    onClick={() => {
                                                        setEditingId(config.id);
                                                        setEditForm({
                                                            provider_name: config.provider_name,
                                                            config_data: config.config_data || {},
                                                            is_active: config.is_active,
                                                            is_default: config.is_default
                                                        });
                                                    }}
                                                    variant="outline"
                                                    size="sm"
                                                >
                                                    <Edit className="h-3 w-3 mr-1" />
                                                    编辑
                                                </Button>

                                                <Button
                                                    onClick={() => handleTestConnection(config.id)}
                                                    variant="outline"
                                                    size="sm"
                                                    disabled={testingId === config.id}
                                                >
                                                    {testingId === config.id ? (
                                                        <>
                                                            <Loader2 className="h-3 w-3 mr-1 animate-spin" />
                                                            测试中
                                                        </>
                                                    ) : (
                                                        <>
                                                            <Brain className="h-3 w-3 mr-1" />
                                                            测试
                                                        </>
                                                    )}
                                                </Button>

                                                {!config.is_default && (
                                                    <Button
                                                        onClick={() => handleSetDefault(config.id)}
                                                        variant="outline"
                                                        size="sm"
                                                    >
                                                        <Star className="h-3 w-3 mr-1" />
                                                        设为默认
                                                    </Button>
                                                )}

                                                <Button
                                                    onClick={() => handleToggleActive(config)}
                                                    variant={config.is_active ? "default" : "outline"}
                                                    size="sm"
                                                >
                                                    {config.is_active ? (
                                                        <>
                                                            <XCircle className="h-3 w-3 mr-1" />
                                                            停用
                                                        </>
                                                    ) : (
                                                        <>
                                                            <CheckCircle className="h-3 w-3 mr-1" />
                                                            激活
                                                        </>
                                                    )}
                                                </Button>

                                                {!config.is_default && !config.is_active && (
                                                    <Button
                                                        onClick={() => handleDelete(config.id)}
                                                        variant="destructive"
                                                        size="sm"
                                                    >
                                                        <Trash2 className="h-3 w-3 mr-1" />
                                                        删除
                                                    </Button>
                                                )}
                                            </div>
                                        )}

                                        {/* 错误信息 */}
                                        {config.error_message && (
                                            <Alert className="border-red-500">
                                                <AlertDescription className="text-xs">
                                                    ⚠️ {config.error_message}
                                                </AlertDescription>
                                            </Alert>
                                        )}
                                    </CardContent>
                                </Card>
                            ))}
                        </div>
                    )}
                </div>
            </DialogContent>
        </Dialog>
    );
}
