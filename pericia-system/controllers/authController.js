const User = require('../models/User');
const jwt = require('jsonwebtoken');

const authController = {
    // Registro de usuário
    register: async (req, res) => {
        try {
            const { nome, email, senha, cpf, telefone, especialidades } = req.body;
            
            const userExiste = await User.findOne({ where: { email } });
            if (userExiste) {
                return res.status(400).json({ error: 'Email já cadastrado' });
            }
            
            const user = await User.create({
                nome,
                email,
                senha,
                cpf,
                telefone,
                especialidades
            });
            
            const token = jwt.sign(
                { id: user.id }, 
                process.env.JWT_SECRET,
                { expiresIn: '7d' }
            );
            
            res.status(201).json({
                user: {
                    id: user.id,
                    nome: user.nome,
                    email: user.email,
                    role: user.role
                },
                token
            });
        } catch (error) {
            res.status(400).json({ error: error.message });
        }
    },
    
    // Login
    login: async (req, res) => {
        try {
            const { email, senha } = req.body;
            
            const user = await User.findOne({ where: { email } });
            if (!user) {
                return res.status(401).json({ error: 'Credenciais inválidas' });
            }
            
            const senhaValida = await user.validarSenha(senha);
            if (!senhaValida) {
                return res.status(401).json({ error: 'Credenciais inválidas' });
            }
            
            if (!user.ativo) {
                return res.status(401).json({ error: 'Usuário inativo' });
            }
            
            const token = jwt.sign(
                { id: user.id },
                process.env.JWT_SECRET,
                { expiresIn: '7d' }
            );
            
            res.json({
                user: {
                    id: user.id,
                    nome: user.nome,
                    email: user.email,
                    role: user.role
                },
                token
            });
        } catch (error) {
            res.status(400).json({ error: error.message });
        }
    },
    
    // Obter perfil
    getProfile: async (req, res) => {
        try {
            res.json(req.user);
        } catch (error) {
            res.status(400).json({ error: error.message });
        }
    },
    
    // Atualizar perfil
    updateProfile: async (req, res) => {
        try {
            const updates = Object.keys(req.body);
            const allowedUpdates = ['nome', 'telefone', 'especialidades'];
            const isValidOperation = updates.every(update => allowedUpdates.includes(update));
            
            if (!isValidOperation) {
                return res.status(400).json({ error: 'Atualizações inválidas' });
            }
            
            updates.forEach(update => req.user[update] = req.body[update]);
            await req.user.save();
            
            res.json(req.user);
        } catch (error) {
            res.status(400).json({ error: error.message });
        }
    }
};

module.exports = authController;
