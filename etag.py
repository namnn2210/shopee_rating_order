import base64
import hashlib
import math


def ct(image_base64):
    def t(e):
        return bytearray.fromhex(e)

    def r():
        if not d:
            return "Fto5o-5ea0sNMlW_75VgGJCv2AcJ"
        e = b"".join(d)
        if h > 1:
            e = u(e)
        else:
            e = bytearray(e)
        return base64.urlsafe_b64encode(bytearray([f]) + e).decode().replace("/", "_").replace("+", "-")

    n = hashlib.sha1(base64.b64decode(image_base64.encode())).hexdigest()
    u = hashlib.md5
    l = 4194304
    d = []
    f = 22
    p = len(image_base64)
    h = math.ceil(p / l)

    for m in range(h):
        chunk = image_base64[m * l: (m + 1) * l]
        d.append(u(chunk.encode()).digest())

    return r()


# Example usage:
base64_image = "/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAA0JCgsKCA0LCgsODg0PEyAVExISEyccHhcgLikxMC4pLSwzOko+MzZGNywtQFdBRkxOUlNSMj5aYVpQYEpRUk//2wBDAQ4ODhMREyYVFSZPNS01T09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT0//wAARCAAPAFADASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwDiopSMLtQ+hKipvkYAuig+2Bmq8aqSd5I44wKcJGUjaVH4Z/nTEPOOMQMR64x/Sm7OP9Q/PfP/ANal3yqN3mr+X/1qTzJOV8xeTjp/9alqPQYyMWO2NgPTGaTY/wDcb8qkSSToJF/Ef/WprKwPMg5+tAWQ3y3/ALjflQVYdVI/Cjnn5+n1pMn1pi0Dax6KfypdjYztOPpSZPqaMn1NAH//2Q=="
result = ct(base64_image)
print(result)
