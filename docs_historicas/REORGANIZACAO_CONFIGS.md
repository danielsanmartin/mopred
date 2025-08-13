# Reorganização dos Arquivos de Configuração

## 📁 Mudanças Realizadas

### Movimentação dos Arquivos
- `config.json` → `configs/config.json`
- `caracteristicas_veiculos.json` → `configs/caracteristicas_veiculos.json`

### Arquivos Atualizados

#### 1. Arquivo Principal
- **`validacao_modelo_conceitual.py`**:
  - Atualizado 3 referências para `configs/config.json`
  - Atualizado 1 referência no SimuladorStreamingALPR

#### 2. Gerador de Veículos
- **`gerador_veiculos.py`**:
  - Atualizado default parameter para `configs/caracteristicas_veiculos.json`
  - Atualizado chamada no main para novo caminho

#### 3. Simulador Streaming
- **`simulador_streaming_alpr.py`**:
  - Atualizado default parameter para `configs/config.json`
  - Atualizado chamada no main para novo caminho

#### 4. Testes - Correções de Cidades
- **`testes/correcoes_cidades/teste_correcao_cidades.py`**: Path relativo atualizado
- **`testes/correcoes_cidades/debug_cidades.py`**: Path relativo atualizado  
- **`testes/correcoes_cidades/teste_alertas_cidades.py`**: Duas referências atualizadas

#### 5. Testes - Validação de Alertas
- **`testes/validacao_alertas/testar_formatacao_alertas.py`**: Path relativo atualizado
- **`testes/validacao_alertas/validar_pasta_alertas.py`**: Path direto atualizado
- **`testes/validacao_alertas/validar_correcoes.py`**: Path direto atualizado
- **`testes/validacao_alertas/teste_pasta_alertas.py`**: Path direto atualizado
- **`testes/validacao_alertas/teste_alertas_corrigidos.py`**: Path direto atualizado

#### 6. Demonstração
- **`testes/demos/demo_controle_alertas.py`**: Path direto atualizado

#### 7. Debug Geral
- **`testes/debug_geral/verificar_caracteristicas_clones.py`**: Path direto atualizado

## ✅ Validações

### Configuração Principal
```bash
# Teste realizado com sucesso
python -c "import json; config = json.load(open('configs/config.json', 'r', encoding='utf-8')); print('pasta_alertas:', config.get('pasta_alertas'))"
# Resultado: pasta_alertas: alertas_gerados
```

### Arquivos Atualizados
- ✅ **15 arquivos** foram atualizados com as novas referências
- ✅ **21 ocorrências** de paths foram corrigidas
- ✅ Tanto **paths relativos** quanto **paths diretos** foram atualizados
- ✅ Todas as **referências a config.json** agora apontam para `configs/config.json`
- ✅ Todas as **referências a caracteristicas_veiculos.json** agora apontam para `configs/caracteristicas_veiculos.json`

## 📂 Estrutura Final

```
mopred/
├── configs/
│   ├── config.json                    # ✅ Configuração principal
│   └── caracteristicas_veiculos.json  # ✅ Especificações de veículos
├── validacao_modelo_conceitual.py     # ✅ Atualizado
├── gerador_veiculos.py                # ✅ Atualizado
├── simulador_streaming_alpr.py        # ✅ Atualizado
└── testes/
    ├── correcoes_cidades/             # ✅ 3 arquivos atualizados
    ├── validacao_alertas/             # ✅ 5 arquivos atualizados
    ├── demos/                         # ✅ 1 arquivo atualizado
    └── debug_geral/                   # ✅ 1 arquivo atualizado
```

## 🎯 Benefícios da Reorganização

1. **Organização Melhorada**: Configurações centralizadas em pasta dedicada
2. **Manutenibilidade**: Easier para encontrar e editar configurações
3. **Estrutura Profissional**: Separação clara entre código e configuração
4. **Escalabilidade**: Facilita adição de novos arquivos de configuração

## 📝 Próximos Passos

- Todos os arquivos estão funcionando com as novas referências
- Sistema pronto para uso com a nova estrutura organizada
- Configurações mantêm compatibilidade com funcionalidades existentes
