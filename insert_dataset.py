#!/usr/bin/env python
# -*- coding: utf-8 -*-

dataset_code = '''    // ==================== DATASET DE LOJAS (SINGLE SOURCE OF TRUTH) ====================
    const STORES = [
      {
        slug: 'zentrix',
        nome: 'Zentrix',
        imageSrc: 'Fachada Zentrix.png',
        loginUrl: 'https://zentrix.grupogarciaseguradoras.com.br/login',
        isBoutique: false,
        chips: ['Gestão', 'Dashboard', 'Integração'],
        diferenciais: [
          'Gestão centralizada de múltiplas operações',
          'Dashboard em tempo real com métricas avançadas',
          'Automação de processos empresariais'
        ]
      },
      {
        slug: 'serra',
        nome: 'Serra',
        imageSrc: 'Fachada serra.png',
        loginUrl: 'https://serra.grupogarciaseguradoras.com.br/login',
        isBoutique: false,
        chips: ['Consultoria', 'Estratégia', 'Análise'],
        diferenciais: [
          'Consultoria estratégica personalizada',
          'Planejamento e execução de campanhas',
          'Análise de mercado e concorrência'
        ]
      },
      {
        slug: 'bliss',
        nome: 'Bliss',
        imageSrc: 'Fachada Bliss.jpeg',
        loginUrl: 'https://bliss.grupogarciaseguradoras.com.br/login',
        isBoutique: false,
        chips: ['Gestão', 'Integrada', 'Automação'],
        diferenciais: [
          'Gestão centralizada de múltiplas operações',
          'Dashboard em tempo real com métricas avançadas',
          'Automação de processos empresariais'
        ]
      },
      {
        slug: 'alleman',
        nome: 'Alleman',
        imageSrc: 'Fachada Alleman.jpeg',
        loginUrl: 'https://alleman.grupogarciaseguradoras.com.br/login',
        isBoutique: false,
        chips: ['Consultoria', 'Campanhas', 'Mercado'],
        diferenciais: [
          'Consultoria estratégica personalizada',
          'Planejamento e execução de campanhas',
          'Otimização de processos comerciais'
        ]
      },
      {
        slug: 'affinity',
        nome: 'Affinity',
        imageSrc: 'Fachada Affinity.jpeg',
        loginUrl: 'https://affinity.grupogarciaseguradoras.com.br/login',
        isBoutique: false,
        chips: ['Conexão', 'Oportunidades', 'Comunidade'],
        diferenciais: [
          'Conexão e rede de profissionais',
          'Oportunidades de negócio qualificadas',
          'Comunidade ativa de especialistas'
        ]
      },
      {
        slug: 'valorize',
        nome: 'Valorize',
        imageSrc: 'Fachada Valorize.jpeg',
        loginUrl: 'https://valorize.grupogarciaseguradoras.com.br/login',
        isBoutique: false,
        chips: ['Reconhecimento', 'Comissões', 'Benefícios'],
        diferenciais: [
          'Programa exclusivo de reconhecimento',
          'Comissões atrativas e competitivas',
          'Benefícios que crescem com seu sucesso'
        ]
      },
      {
        slug: 'as-sure',
        nome: 'AS.SURE',
        imageSrc: 'fachada_assure.jpeg',
        loginUrl: 'https://assury.grupogarciaseguradoras.com.br/login',
        isBoutique: false,
        chips: ['Segurança', 'Compliance', 'Monitoramento'],
        diferenciais: [
          'Segurança e cobertura completa',
          'Segurança integrada e automatizada',
          'Monitoramento 24/7 em tempo real'
        ]
      },
      {
        slug: 'diplan',
        nome: 'Diplan',
        imageSrc: 'Fachada Diplan.png',
        loginUrl: null,
        isBoutique: true,
        chips: ['VIP', 'Premium', 'Exclusivo'],
        diferenciais: [
          'Atendimento VIP com dedicação exclusiva',
          'Estratégias customizadas para alto padrão',
          'Consultoria estratégica premium'
        ]
      }
    ];

'''

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Insert STORES dataset before DOMContentLoaded
insert_pos = content.find('    document.addEventListener(\'DOMContentLoaded\'')
if insert_pos != -1:
    new_content = content[:insert_pos] + dataset_code + content[insert_pos:]
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Dataset inserted successfully!")
else:
    print("Could not find DOMContentLoaded")
