import socket
import re

SUPPORTED_RECORDS = {"SOA", "NS", "A", "AAAA", "CNAME", "MX"}


def parse_line(check_res):
    rtype, left, right = check_res
    record = {}
    for field in left:
        if field.isnumeric():
            record["ttl"] = int(field)
        elif field != "IN":
            record["domain_name"] = field
    record["rdata"] = ' '.join(right)
    return rtype, record


def check_record(line: str):
    index = 0
    fields = line.split()
    for field in fields:
        if field in SUPPORTED_RECORDS:
            return field, fields[:index], fields[index + 1:]
        index += 1
    return False


def parse_zone_file(zone_file):
    for line in zone_file:
        processed_line = re.sub(";.*", "", line)
        if processed_line != "\n":
            check_res = check_record(processed_line)
            if check_res:
                yield parse_line(check_res)


def main():
    parse_zone_file(open("usaaa.ru"))


if __name__ == '__main__':
    main()
