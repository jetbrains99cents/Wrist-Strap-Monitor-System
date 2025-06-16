#include "database.h"
#include "logger.h"
#include <LittleFS.h>
#include <sys/time.h>

void Database::begin() {
    if (!LittleFS.exists(_queue_dir)) {
        Logger::get_instance().log_info("Queue directory not found, creating '%s'...", _queue_dir);
        if (LittleFS.mkdir(_queue_dir)) {
            Logger::get_instance().log_info("Queue directory created.");
        } else {
            Logger::get_instance().log_error("Failed to create queue directory.");
        }
    } else {
        Logger::get_instance().log_info("Queue directory '%s' found.", _queue_dir);
    }
    Logger::get_instance().log_info("Database contains %d queued messages.", get_queue_size());
}

bool Database::append_reading(const char* json_payload) {
    timeval tv;
    gettimeofday(&tv, nullptr);
    uint64_t timestamp_ms = (uint64_t)tv.tv_sec * 1000L + (uint64_t)tv.tv_usec / 1000L;
    
    String filename = String(_queue_dir) + "/" + String(timestamp_ms) + ".json";
    
    File file = LittleFS.open(filename, "w");
    if (!file) {
        Logger::get_instance().log_error("Failed to open file for writing: %s", filename.c_str());
        return false;
    }
    
    if (file.print(json_payload)) {
        Logger::get_instance().log_info("Appended new reading to queue: %s", filename.c_str());
        file.close();
        return true;
    } else {
        Logger::get_instance().log_error("Write failed for file: %s", filename.c_str());
        file.close();
        return false;
    }
}

bool Database::retrieve_oldest_reading_filename(String& filename) {
    File root = LittleFS.open(_queue_dir);
    if (!root) {
        Logger::get_instance().log_error("Failed to open queue directory.");
        return false;
    }

    File file = root.openNextFile();
    if (!file) {
        // Queue is empty
        root.close();
        return false;
    }

    filename = file.name();
    // Continue through files to find the lexicographically smallest (oldest) name
    while (File nextFile = root.openNextFile()) {
        if (String(nextFile.name()) < filename) {
            filename = nextFile.name();
        }
        nextFile.close();
    }
    file.close();
    root.close();

    filename = String(_queue_dir) + "/" + filename;
    return true;
}

bool Database::read_file(const String& filename, char* buffer, size_t buffer_size) {
    File file = LittleFS.open(filename, "r");
    if (!file) {
        Logger::get_instance().log_error("Failed to read file: %s", filename.c_str());
        return false;
    }
    size_t bytes_read = file.readBytes(buffer, buffer_size - 1);
    buffer[bytes_read] = '\0'; // Null-terminate the string
    file.close();
    return true;
}

bool Database::delete_file(const String& filename) {
    if (LittleFS.remove(filename)) {
        Logger::get_instance().log_info("Deleted sent message from queue: %s", filename.c_str());
        return true;
    } else {
        Logger::get_instance().log_error("Failed to delete file: %s", filename.c_str());
        return false;
    }
}

int Database::get_queue_size() {
    int count = 0;
    File root = LittleFS.open(_queue_dir);
    if (root) {
        File file = root.openNextFile();
        while(file){
            count++;
            file = root.openNextFile();
        }
        root.close();
    }
    return count;
}

bool Database::is_queue_empty() {
    return get_queue_size() == 0;
}