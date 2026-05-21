import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def enviar_resultado(email_usuario, nome_usuario, resultado_zona, pontuacao, mensagem):
    # Configurações do servidor SMTP (Gmail)
    # Nota: O usuário precisará configurar uma "Senha de App" no Gmail
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    remetente = "mentecheck2025@gmail.com"
    # A senha deve ser uma Senha de App gerada na conta Google
    # Por segurança, usaremos uma variável ou placeholder
    senha_app = "SUA_SENHA_DE_APP_AQUI" 

    assunto = "Este resultado não substitui uma consulta com profissional, procure seu médico"
    
    corpo = f"""
    Olá, {nome_usuario}!
    
    Aqui está o resultado da sua avaliação no MenteCheck:
    
    --------------------------------------------------
    RESULTADO: {resultado_zona}
    PONTUAÇÃO: {pontuacao:.0f}/50
    MENSAGEM: {mensagem}
    --------------------------------------------------
    
    IMPORTANTE:
    Este relatório é uma ferramenta de autoavaliação complementar baseada nos critérios do DSM-5 e CID-11.
    Ele NÃO substitui um diagnóstico clínico realizado por um profissional de saúde mental.
    
    Recomendamos que você leve este resultado ao seu médico ou psicólogo para uma discussão detalhada.
    
    Em caso de crise imediata, procure o serviço de emergência mais próximo ou ligue 188 (CVV).
    
    Atenciosamente,
    Equipe MenteCheck
    """

    try:
        # Criar a mensagem
        msg = MIMEMultipart()
        msg['From'] = remetente
        msg['To'] = f"{email_usuario}, {remetente}" # Envia para o usuário e cópia para você
        msg['Subject'] = assunto
        msg.attach(MIMEText(corpo, 'plain'))

        # Conectar e enviar
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        # server.login(remetente, senha_app) # Comentado até que o usuário forneça a senha
        # server.sendmail(remetente, [email_usuario, remetente], msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")
        return False
