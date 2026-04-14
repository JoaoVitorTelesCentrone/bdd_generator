# Story: Switch channel recommendations to Vitess
# Model: flash | Score: 5.4/10

Cenário: Usuário autenticado visualiza recomendações consistentes e integrais
  Dado que o usuário "ativo_variado@exemplo.com" está autenticado
    E o usuário "ativo_variado@exemplo.com" possui histórico de seguimento e visualização de canais como "Canal de Tecnologia" e "Canal de Notícias"
    E o serviço de recomendações Vitess está operacional
  Quando eu navego para a página "/recommendations"
  Então eu vejo a seção de recomendações "#recommendations-section"
    E eu vejo até 10 canais recomendados na lista "#recommendations-list"
    E o canal "Canal de Tecnologia Avançada" é exibido na lista "#recommendations-list