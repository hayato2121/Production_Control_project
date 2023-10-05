#Url設定
def my_custom_context(request):
    # ここで protocol と domain を設定する
    protocol = 'http' if request.is_secure() else 'https'
    domain = request.get_host()
    
    return {
        'protocol': protocol,
        'domain': domain,
    }