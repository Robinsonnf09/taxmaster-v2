const sequelize = require('./config/database');
const User = require('./models/User');
const Oportunidade = require('./models/Oportunidade');
const Candidatura = require('./models/Candidatura');

// Relacionamentos
User.hasMany(Candidatura, { foreignKey: 'userId' });
Candidatura.belongsTo(User, { foreignKey: 'userId' });

Oportunidade.hasMany(Candidatura, { foreignKey: 'oportunidadeId' });
Candidatura.belongsTo(Oportunidade, { foreignKey: 'oportunidadeId' });

async function initDatabase() {
    try {
        console.log('🔄 Conectando ao banco de dados...');
        
        await sequelize.authenticate();
        console.log('✓ Conexão estabelecida com sucesso!');
        
        console.log('🔄 Sincronizando modelos...');
        await sequelize.sync({ force: false });
        console.log('✓ Modelos sincronizados!');
        
        // Verificar se já existe usuário admin
        const adminExiste = await User.findOne({ where: { email: 'admin@taxmaster.com' } });
        
        if (!adminExiste) {
            console.log('🔄 Criando usuário administrador...');
            await User.create({
                nome: 'Administrador',
                email: 'admin@taxmaster.com',
                senha: 'admin123',
                role: 'admin',
                especialidades: ['Contábil', 'Financeira']
            });
            console.log('✓ Usuário administrador criado!');
            console.log('  Email: admin@taxmaster.com');
            console.log('  Senha: admin123');
        }
        
        // Importar oportunidades do scraper
        console.log('🔄 Importando oportunidades do scraper...');
        const fs = require('fs');
        const path = require('path');
        
        const scrapersDir = path.join(__dirname, 'scrapers');
        const files = fs.readdirSync(scrapersDir)
            .filter(f => f.startsWith('oportunidades_demo_') && f.endsWith('.json'))
            .sort()
            .reverse();
        
        if (files.length > 0) {
            const filepath = path.join(scrapersDir, files[0]);
            const data = JSON.parse(fs.readFileSync(filepath, 'utf-8'));
            
            for (const opp of data) {
                const existe = await Oportunidade.findOne({ where: { processo: opp.processo } });
                if (!existe) {
                    await Oportunidade.create(opp);
                }
            }
            console.log(`✓ ${data.length} oportunidades importadas!`);
        }
        
        console.log('\n╔═══════════════════════════════════════════════════════════╗');
        console.log('║         BANCO DE DADOS INICIALIZADO COM SUCESSO!         ║');
        console.log('╚═══════════════════════════════════════════════════════════╝\n');
        
        process.exit(0);
    } catch (error) {
        console.error('❌ Erro ao inicializar banco:', error);
        process.exit(1);
    }
}

initDatabase();
