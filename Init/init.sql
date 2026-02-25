create table ai_analysis_records
(
    id             int auto_increment comment '记录ID'
        primary key,
    ts_code        varchar(20)                    not null comment '股票代码',
    stock_name     varchar(100)                   not null comment '股票名称',
    recommendation enum ('buy', 'sell', 'hold')   not null comment '推荐操作',
    confidence     float                          not null comment '置信度(0-1)',
    target_price   float                          null comment '目标价格',
    risk_level     enum ('low', 'medium', 'high') not null comment '风险等级',
    reasons        text                           null comment '推荐理由JSON',
    ai_provider    varchar(50)                    null comment 'AI提供者',
    model_name     varchar(100)                   null comment '使用的模型名称',
    analysis_data  text                           null comment '分析用的数据JSON',
    success        tinyint(1)                     null comment '分析是否成功',
    error_message  text                           null comment '错误信息',
    response_time  float                          null comment '响应时间(秒)',
    created_at     datetime                       null comment '创建时间'
);

create index idx_ai_analysis_created_at
    on ai_analysis_records (created_at);

create index idx_ai_analysis_provider
    on ai_analysis_records (ai_provider);

create index idx_ai_analysis_recommendation
    on ai_analysis_records (recommendation);

create index idx_ai_analysis_ts_code_created
    on ai_analysis_records (ts_code, created_at);

create table ai_config
(
    id             int auto_increment
        primary key,
    provider_type  varchar(50)  not null,
    provider_name  varchar(100) not null,
    config_data    json         null,
    is_active      tinyint(1)   null,
    is_default     tinyint(1)   null,
    status         varchar(20)  null,
    last_test_time datetime     null,
    error_message  text         null,
    created_at     datetime     null,
    updated_at     datetime     null
);

create table alert_rules
(
    id                     int auto_increment comment '规则ID'
        primary key,
    rule_name              varchar(100) not null comment '规则名称',
    ts_code                varchar(20)  not null comment '股票代码',
    rule_type              varchar(50)  not null comment '规则类型',
    condition_type         varchar(20)  not null comment '条件类型',
    threshold_value        float        not null comment '阈值',
    comparison_operator    varchar(10)  not null comment '比较运算符',
    alert_level            varchar(20)  null comment '预警级别',
    alert_message_template text         null comment '预警消息模板',
    is_enabled             tinyint(1)   null comment '是否启用',
    is_active              tinyint(1)   null comment '是否活跃',
    trigger_count          int          null comment '触发次数',
    last_triggered_at      datetime     null comment '最后触发时间',
    created_at             datetime     null comment '创建时间',
    updated_at             datetime     null comment '更新时间',
    extra_config           text         null comment '扩展配置JSON'
);

create index idx_alert_rules_active
    on alert_rules (is_active);

create index idx_alert_rules_created_at
    on alert_rules (created_at);

create index idx_alert_rules_ts_code
    on alert_rules (ts_code);

create index idx_alert_rules_type_enabled
    on alert_rules (rule_type, is_enabled);

create table data_source_config
(
    id             int auto_increment
        primary key,
    source_type    varchar(50)  not null,
    source_name    varchar(100) not null,
    config_data    json         null,
    is_active      tinyint(1)   null,
    is_default     tinyint(1)   null,
    status         varchar(20)  null,
    last_test_time datetime     null,
    error_message  text         null,
    created_at     datetime     null,
    updated_at     datetime     null
);

create table risk_alerts
(
    id               int auto_increment
        primary key,
    ts_code          varchar(20)                           not null comment '股票代码',
    alert_type       varchar(50)                           not null comment '预警类型',
    alert_level      varchar(20)                           not null comment '预警级别',
    alert_message    text                                  null comment '预警消息',
    risk_value       float                                 null comment '风险值',
    threshold_value  float                                 null comment '阈值',
    current_price    float                                 null comment '当前价格',
    position_size    float                                 null comment '持仓数量',
    portfolio_weight float                                 null comment '组合权重',
    is_active        tinyint(1)                            null comment '是否活跃',
    is_resolved      tinyint(1)                            null comment '是否已解决',
    created_at       datetime                              null comment '创建时间',
    resolved_at      datetime                              null comment '解决时间',
    rule_id          int                                   null comment '关联的预警规则ID',
    trigger_source   varchar(20) default 'auto'            null comment '触发源: auto/manual/api/system',
    alert_status     varchar(20) default 'active'          null comment '预警状态: active/resolved/ignored/pending',
    updated_at       datetime    default CURRENT_TIMESTAMP null on update CURRENT_TIMESTAMP comment '更新时间',
    ignored_at       datetime                              null comment '忽略时间',
    extra_data       text                                  null comment '扩展数据JSON',
    resolution_note  text                                  null comment '解决备注',
    is_ignored       tinyint(1)  default 0                 null comment '是否已忽略',
    constraint fk_risk_alerts_rule_id
        foreign key (rule_id) references alert_rules (id)
);

create index idx_risk_alerts_created_at
    on risk_alerts (created_at);

create index idx_risk_alerts_level_active
    on risk_alerts (alert_level, is_active);

create index idx_risk_alerts_level_status
    on risk_alerts (alert_level, alert_status);

create index idx_risk_alerts_rule_id
    on risk_alerts (rule_id);

create index idx_risk_alerts_source
    on risk_alerts (trigger_source);

create index idx_risk_alerts_ts_code_type
    on risk_alerts (ts_code, alert_type);

create index idx_risk_alerts_updated_at
    on risk_alerts (updated_at);

create table stock_basic
(
    ts_code   varchar(20)  not null comment 'TS代码'
        primary key,
    symbol    varchar(20)  null comment '股票代码',
    name      varchar(100) null comment '股票名称',
    area      varchar(100) null comment '地域',
    industry  varchar(100) null comment '所属行业',
    list_date date         null comment '上市日期'
);

create table stock_daily_basic
(
    ts_code         varchar(20)    not null comment 'TS股票代码',
    trade_date      date           not null comment '交易日期',
    close           decimal(10, 2) null comment '当日收盘价',
    turnover_rate   decimal(10, 2) null comment '换手率（%）',
    turnover_rate_f decimal(10, 2) null comment '换手率（自由流通股）',
    volume_ratio    decimal(10, 2) null comment '量比',
    pe              decimal(10, 2) null comment '市盈率',
    pe_ttm          decimal(10, 2) null comment '市盈率（TTM）',
    pb              decimal(10, 2) null comment '市净率',
    ps              decimal(10, 2) null comment '市销率',
    ps_ttm          decimal(10, 2) null comment '市销率（TTM）',
    dv_ratio        decimal(10, 2) null comment '股息率（%）',
    dv_ttm          decimal(10, 2) null comment '股息率（TTM）（%）',
    total_share     decimal(20, 2) null comment '总股本（万股）',
    float_share     decimal(20, 2) null comment '流通股本（万股）',
    free_share      decimal(20, 2) null comment '自由流通股本（万）',
    total_mv        decimal(20, 2) null comment '总市值（万元）',
    circ_mv         decimal(20, 2) null comment '流通市值（万元）',
    primary key (ts_code, trade_date)
);

create table stock_daily_history
(
    ts_code    varchar(20)    not null comment '股票代码',
    trade_date date           not null comment '交易日期',
    open       decimal(10, 2) null comment '开盘价',
    high       decimal(10, 2) null comment '最高价',
    low        decimal(10, 2) null comment '最低价',
    close      decimal(10, 2) null comment '收盘价',
    pre_close  decimal(10, 2) null comment '昨收价',
    change_c   decimal(10, 2) null comment '涨跌额',
    pct_chg    decimal(10, 2) null comment '涨跌幅',
    vol        bigint         null comment '成交量（手）',
    amount     decimal(20, 2) null comment '成交额（千元）',
    primary key (ts_code, trade_date)
);

create table stock_moneyflow
(
    ts_code         varchar(20)    not null comment '股票代码',
    trade_date      date           not null comment '交易日期',
    buy_sm_vol      decimal(20, 2) null comment '小单买入量（手）',
    buy_sm_amount   decimal(20, 2) null comment '小单买入金额（万元）',
    sell_sm_vol     decimal(20, 2) null comment '小单卖出量（手）',
    sell_sm_amount  decimal(20, 2) null comment '小单卖出金额（万元）',
    buy_md_vol      decimal(20, 2) null comment '中单买入量（手）',
    buy_md_amount   decimal(20, 2) null comment '中单买入金额（万元）',
    sell_md_vol     decimal(20, 2) null comment '中单卖出量（手）',
    sell_md_amount  decimal(20, 2) null comment '中单卖出金额（万元）',
    buy_lg_vol      decimal(20, 2) null comment '大单买入量（手）',
    buy_lg_amount   decimal(20, 2) null comment '大单买入金额（万元）',
    sell_lg_vol     decimal(20, 2) null comment '大单卖出量（手）',
    sell_lg_amount  decimal(20, 2) null comment '大单卖出金额（万元）',
    buy_elg_vol     decimal(20, 2) null comment '特大单买入量（手）',
    buy_elg_amount  decimal(20, 2) null comment '特大单买入金额（万元）',
    sell_elg_vol    decimal(20, 2) null comment '特大单卖出量（手）',
    sell_elg_amount decimal(20, 2) null comment '特大单卖出金额（万元）',
    net_mf_vol      decimal(20, 2) null comment '净流入量（手）',
    net_mf_amount   decimal(20, 2) null comment '净流入额（万元）',
    primary key (ts_code, trade_date)
);

create table system_configs
(
    id           int auto_increment
        primary key,
    config_key   varchar(100) not null comment '配置键',
    config_value text         null comment '配置值(加密存储)',
    config_type  varchar(20)  null comment '配置类型:string/json/encrypted',
    description  varchar(200) null comment '配置描述',
    is_encrypted tinyint(1)   null comment '是否加密存储',
    is_active    tinyint(1)   null comment '是否启用',
    created_at   datetime     null comment '创建时间',
    updated_at   datetime     null comment '更新时间',
    constraint config_key
        unique (config_key)
);

create table watchlist
(
    id        int auto_increment
        primary key,
    ts_code   varchar(20)  not null comment '股票代码',
    symbol    varchar(10)  null comment '简称',
    name      varchar(50)  null comment '股票名称',
    note      varchar(200) null comment '用户备注',
    added_at  datetime     null comment '添加时间',
    last_sync datetime     null comment '最后同步时间',
    constraint ix_watchlist_ts_code
        unique (ts_code)
);

create table webhook_configs
(
    id                 int auto_increment comment '配置ID'
        primary key,
    webhook_type       varchar(50)  not null comment 'Webhook类型',
    webhook_name       varchar(100) not null comment 'Webhook名称',
    config_data        json         null comment '配置数据（URL、密钥、模板等）',
    is_enabled         tinyint(1)   null comment '是否启用',
    is_default         tinyint(1)   null comment '是否为默认Webhook',
    status             varchar(20)  null comment '连接状态：成功、失败、未测试',
    last_test_time     datetime     null comment '最后测试时间',
    error_message      text         null comment '错误信息',
    alert_levels       json         null comment '启用的预警级别：[''low'', ''medium'', ''high'', ''critical'']',
    message_template   text         null comment '自定义消息模板',
    include_stock_info tinyint(1)   null comment '是否包含股票信息',
    include_rule_info  tinyint(1)   null comment '是否包含规则信息',
    retry_count        int          null comment '重试次数',
    retry_interval     int          null comment '重试间隔（秒）',
    created_at         datetime     null comment '创建时间',
    updated_at         datetime     null comment '更新时间'
);
