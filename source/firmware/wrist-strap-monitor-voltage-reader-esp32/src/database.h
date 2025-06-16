#ifndef DATABASE_H
#define DATABASE_H

#include <Arduino.h>

class Database {
public:
    void begin();
    bool append_reading(const char* json_payload);
    bool retrieve_oldest_reading_filename(String& filename);
    bool read_file(const String& filename, char* buffer, size_t buffer_size);
    bool delete_file(const String& filename);
    int get_queue_size();
    bool is_queue_empty();

private:
    const char* _queue_dir = "/data_queue";
};

#endif // DATABASE_H