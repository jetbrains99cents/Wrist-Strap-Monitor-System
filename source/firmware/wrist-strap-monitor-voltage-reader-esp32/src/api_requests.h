#ifndef API_REQUESTS_H
#define API_REQUESTS_H

class Mediator;

class ApiRequests {
public:
    void init(Mediator* mediator);
    void request_time_sync();

private:
    Mediator* _mediator;
};

#endif // API_REQUESTS_H