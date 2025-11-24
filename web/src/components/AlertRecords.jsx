import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { AlertTriangle, CheckCircle, XCircle, Clock, Filter, RefreshCw, Bell } from 'lucide-react';
import api from '@/services/api';

const AlertRecords = () => {
    const [loading, setLoading] = useState(true);
    const [stats, setStats] = useState(null);
    const [records, setRecords] = useState([]);
    const [options, setOptions] = useState({ types: {}, levels: {}, statuses: {} });
    const [filters, setFilters] = useState({
        alert_type: 'all',
        alert_level: 'all',
        alert_status: 'all'
    });
    const [pagination, setPagination] = useState({
        page: 1,
        per_page: 20,
        total: 0,
        pages: 1
    });

    // Fetch data on mount and when filters/pagination change
    useEffect(() => {
        fetchData();
    }, [filters, pagination.page]);

    // Initial fetch for options and stats
    useEffect(() => {
        fetchOptions();
        fetchStats();
    }, []);

    const fetchOptions = async () => {
        try {
            const response = await api.getAlertOptions();
            if (response && response.data) {
                setOptions({
                    types: response.data.alert_types || {},
                    levels: response.data.alert_levels || {},
                    statuses: response.data.alert_statuses || {}
                });
            }
        } catch (error) {
            console.error("Failed to fetch alert options:", error);
        }
    };

    const fetchStats = async () => {
        try {
            const response = await api.getAlertStats(7); // Last 7 days
            if (response && response.data) {
                setStats(response.data);
            }
        } catch (error) {
            console.error("Failed to fetch alert stats:", error);
        }
    };

    const fetchData = async () => {
        setLoading(true);
        try {
            const params = {
                page: pagination.page,
                per_page: pagination.per_page
            };

            if (filters.alert_type !== 'all') params.alert_type = filters.alert_type;
            if (filters.alert_level !== 'all') params.alert_level = filters.alert_level;
            if (filters.alert_status !== 'all') params.alert_status = filters.alert_status;

            const response = await api.getAlertRecords(params);
            if (response && response.data) {
                setRecords(response.data.records || []);
                setPagination({
                    page: response.data.pagination.page,
                    per_page: response.data.pagination.per_page,
                    total: response.data.pagination.total,
                    pages: response.data.pagination.pages
                });
            }
        } catch (error) {
            console.error("Failed to fetch alert records:", error);
        } finally {
            setLoading(false);
        }
    };

    const handleResolve = async (id) => {
        try {
            await api.resolveAlert(id, "Resolved via dashboard");
            fetchData();
            fetchStats();
        } catch (error) {
            console.error("Failed to resolve alert:", error);
        }
    };

    const handleIgnore = async (id) => {
        try {
            await api.ignoreAlert(id, "Ignored via dashboard");
            fetchData();
            fetchStats();
        } catch (error) {
            console.error("Failed to ignore alert:", error);
        }
    };

    const getLevelBadgeColor = (level) => {
        switch (level) {
            case 'critical': return 'bg-red-100 text-red-800 border-red-200';
            case 'high': return 'bg-orange-100 text-orange-800 border-orange-200';
            case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
            case 'low': return 'bg-blue-100 text-blue-800 border-blue-200';
            default: return 'bg-gray-100 text-gray-800 border-gray-200';
        }
    };

    const getStatusBadgeColor = (status) => {
        switch (status) {
            case 'active': return 'bg-red-50 text-red-700 border-red-200';
            case 'resolved': return 'bg-green-50 text-green-700 border-green-200';
            case 'ignored': return 'bg-gray-50 text-gray-700 border-gray-200';
            default: return 'bg-gray-50 text-gray-700 border-gray-200';
        }
    };

    return (
        <div className="space-y-6">
            {/* Statistics Cards */}
            {stats && (
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <Card>
                        <CardContent className="pt-6">
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="text-sm font-medium text-gray-500">Total Alerts (7d)</p>
                                    <h3 className="text-2xl font-bold text-gray-900 mt-1">{stats.total_alerts}</h3>
                                </div>
                                <div className="p-3 bg-blue-50 rounded-full">
                                    <Bell className="w-5 h-5 text-blue-600" />
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                    <Card>
                        <CardContent className="pt-6">
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="text-sm font-medium text-gray-500">Active</p>
                                    <h3 className="text-2xl font-bold text-red-600 mt-1">{stats.active_alerts}</h3>
                                </div>
                                <div className="p-3 bg-red-50 rounded-full">
                                    <AlertTriangle className="w-5 h-5 text-red-600" />
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                    <Card>
                        <CardContent className="pt-6">
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="text-sm font-medium text-gray-500">Resolved</p>
                                    <h3 className="text-2xl font-bold text-green-600 mt-1">{stats.resolved_alerts}</h3>
                                </div>
                                <div className="p-3 bg-green-50 rounded-full">
                                    <CheckCircle className="w-5 h-5 text-green-600" />
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                    <Card>
                        <CardContent className="pt-6">
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="text-sm font-medium text-gray-500">Ignored</p>
                                    <h3 className="text-2xl font-bold text-gray-600 mt-1">{stats.ignored_alerts}</h3>
                                </div>
                                <div className="p-3 bg-gray-50 rounded-full">
                                    <XCircle className="w-5 h-5 text-gray-600" />
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                </div>
            )}

            <Card>
                <CardHeader className="pb-3">
                    <div className="flex items-center justify-between">
                        <div>
                            <CardTitle>Alert History</CardTitle>
                            <CardDescription>View and manage stock alerts</CardDescription>
                        </div>
                        <Button variant="outline" size="sm" onClick={() => { fetchData(); fetchStats(); }}>
                            <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
                            Refresh
                        </Button>
                    </div>
                </CardHeader>
                <CardContent>
                    {/* Filters */}
                    <div className="flex flex-wrap gap-4 mb-6">
                        <div className="w-40">
                            <Select
                                value={filters.alert_type}
                                onValueChange={(value) => setFilters({ ...filters, alert_type: value })}
                            >
                                <SelectTrigger>
                                    <SelectValue placeholder="Alert Type" />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="all">All Types</SelectItem>
                                    {Object.entries(options.types).map(([key, label]) => (
                                        <SelectItem key={key} value={key}>{label}</SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>
                        <div className="w-40">
                            <Select
                                value={filters.alert_level}
                                onValueChange={(value) => setFilters({ ...filters, alert_level: value })}
                            >
                                <SelectTrigger>
                                    <SelectValue placeholder="Alert Level" />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="all">All Levels</SelectItem>
                                    {Object.entries(options.levels).map(([key, label]) => (
                                        <SelectItem key={key} value={key}>{label}</SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>
                        <div className="w-40">
                            <Select
                                value={filters.alert_status}
                                onValueChange={(value) => setFilters({ ...filters, alert_status: value })}
                            >
                                <SelectTrigger>
                                    <SelectValue placeholder="Status" />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="all">All Statuses</SelectItem>
                                    {Object.entries(options.statuses).map(([key, label]) => (
                                        <SelectItem key={key} value={key}>{label}</SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>
                    </div>

                    {/* Table */}
                    <div className="rounded-md border">
                        <table className="w-full text-sm text-left">
                            <thead className="bg-gray-50 text-gray-500 font-medium">
                                <tr>
                                    <th className="px-4 py-3">Time</th>
                                    <th className="px-4 py-3">Stock</th>
                                    <th className="px-4 py-3">Type</th>
                                    <th className="px-4 py-3">Level</th>
                                    <th className="px-4 py-3">Message</th>
                                    <th className="px-4 py-3">Status</th>
                                    <th className="px-4 py-3 text-right">Actions</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-100">
                                {loading ? (
                                    <tr>
                                        <td colSpan="7" className="px-4 py-8 text-center text-gray-500">
                                            Loading records...
                                        </td>
                                    </tr>
                                ) : records.length === 0 ? (
                                    <tr>
                                        <td colSpan="7" className="px-4 py-8 text-center text-gray-500">
                                            No alert records found
                                        </td>
                                    </tr>
                                ) : (
                                    records.map((record) => (
                                        <tr key={record.id} className="hover:bg-gray-50">
                                            <td className="px-4 py-3 text-gray-500 whitespace-nowrap">
                                                {new Date(record.created_at).toLocaleString()}
                                            </td>
                                            <td className="px-4 py-3 font-medium">
                                                {record.ts_code}
                                            </td>
                                            <td className="px-4 py-3">
                                                {record.alert_type_name}
                                            </td>
                                            <td className="px-4 py-3">
                                                <Badge variant="outline" className={getLevelBadgeColor(record.alert_level)}>
                                                    {record.alert_level_name}
                                                </Badge>
                                            </td>
                                            <td className="px-4 py-3 max-w-xs truncate" title={record.alert_message}>
                                                {record.alert_message}
                                            </td>
                                            <td className="px-4 py-3">
                                                <Badge variant="outline" className={getStatusBadgeColor(record.alert_status)}>
                                                    {record.alert_status_name}
                                                </Badge>
                                            </td>
                                            <td className="px-4 py-3 text-right space-x-2">
                                                {record.alert_status === 'active' && (
                                                    <>
                                                        <Button
                                                            variant="ghost"
                                                            size="sm"
                                                            className="h-8 px-2 text-green-600 hover:text-green-700 hover:bg-green-50"
                                                            onClick={() => handleResolve(record.id)}
                                                        >
                                                            Resolve
                                                        </Button>
                                                        <Button
                                                            variant="ghost"
                                                            size="sm"
                                                            className="h-8 px-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100"
                                                            onClick={() => handleIgnore(record.id)}
                                                        >
                                                            Ignore
                                                        </Button>
                                                    </>
                                                )}
                                            </td>
                                        </tr>
                                    ))
                                )}
                            </tbody>
                        </table>
                    </div>

                    {/* Pagination */}
                    {pagination.pages > 1 && (
                        <div className="flex items-center justify-between mt-4">
                            <div className="text-sm text-gray-500">
                                Showing {(pagination.page - 1) * pagination.per_page + 1} to {Math.min(pagination.page * pagination.per_page, pagination.total)} of {pagination.total} results
                            </div>
                            <div className="flex space-x-2">
                                <Button
                                    variant="outline"
                                    size="sm"
                                    disabled={pagination.page === 1}
                                    onClick={() => setPagination({ ...pagination, page: pagination.page - 1 })}
                                >
                                    Previous
                                </Button>
                                <Button
                                    variant="outline"
                                    size="sm"
                                    disabled={pagination.page === pagination.pages}
                                    onClick={() => setPagination({ ...pagination, page: pagination.page + 1 })}
                                >
                                    Next
                                </Button>
                            </div>
                        </div>
                    )}
                </CardContent>
            </Card>
        </div>
    );
};

export default AlertRecords;
