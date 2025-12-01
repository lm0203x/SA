/**
 * 预警管理组件 - 包含预警规则和Webhook配置的标签页
 */

import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Bell, Webhook } from 'lucide-react';
import AlertRules from './AlertRules';
import WebhookConfig from './WebhookConfig';

export default function AlertManagement() {
    const [activeTab, setActiveTab] = useState('rules'); // 'rules' | 'webhook'

    return (
        <div className="space-y-6">
            {/* 标签页导航 */}
            <div className="flex gap-2 border-b border-gray-200 pb-0">
                <Button
                    variant={activeTab === 'rules' ? 'default' : 'ghost'}
                    className={`rounded-b-none px-6 py-2 ${activeTab === 'rules'
                            ? 'border-b-2 border-blue-500 bg-white text-blue-600 font-semibold shadow-none'
                            : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                        }`}
                    onClick={() => setActiveTab('rules')}
                >
                    <Bell className="h-4 w-4 mr-2" />
                    预警规则
                </Button>
                <Button
                    variant={activeTab === 'webhook' ? 'default' : 'ghost'}
                    className={`rounded-b-none px-6 py-2 ${activeTab === 'webhook'
                            ? 'border-b-2 border-blue-500 bg-white text-blue-600 font-semibold shadow-none'
                            : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                        }`}
                    onClick={() => setActiveTab('webhook')}
                >
                    <Webhook className="h-4 w-4 mr-2" />
                    Webhook配置
                </Button>
            </div>

            {/* 内容区域 */}
            <div>
                {activeTab === 'rules' && <AlertRules />}
                {activeTab === 'webhook' && <WebhookConfig />}
            </div>
        </div>
    );
}
