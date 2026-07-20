#ifndef SENTINEL_AGENT_METRIC_COLLECTOR_H_
#define SENTINEL_AGENT_METRIC_COLLECTOR_H_

class MetricCollector{
    public:
    virtual ~MetricCollector() = default;
    virtual const char* Name() const = 0;
    virtual double Sample() = 0;
};
#endif