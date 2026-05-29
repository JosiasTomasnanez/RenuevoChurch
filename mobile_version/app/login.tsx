import { useRouter } from 'expo-router';
import { useEffect, useState } from 'react';
import { Platform, StyleSheet, Text, TextInput, TouchableOpacity, View } from 'react-native';
import { useAuth } from './_layout';

export default function LoginPage() {
  const router = useRouter();
  const { setIsAuthenticated } = useAuth();
  const [password, setPassword] = useState('');
  const [loginError, setLoginError] = useState('');

  useEffect(() => {
    if (Platform.OS !== 'web') {
      router.replace({ pathname: '/' });
    }
  }, [router]);

  const handleLogin = () => {
    const claveSegura = process.env.EXPO_PUBLIC_WEB_PASSWORD;

    if (!claveSegura) {
      setLoginError('Error de configuración: falta la contraseña de acceso web.');
      setPassword('');
      return;
    }

    if (password.trim() === claveSegura) {
      setIsAuthenticated(true);
      router.replace({ pathname: '/' });
      setLoginError('');
      setPassword('');
    } else {
      setLoginError('Contraseña incorrecta para el acceso Web.');
      setPassword('');
    }
  };

  return (
    <View style={styles.container}>
      <View style={styles.card}>
        <Text style={styles.title}>Renuevo Church</Text>
        <Text style={styles.subtitle}>Acceso Web Interno</Text>

        <TextInput
          placeholder="Contraseña"
          placeholderTextColor="#999"
          secureTextEntry
          value={password}
          onChangeText={setPassword}
          style={styles.input}
          onSubmitEditing={handleLogin}
          autoCapitalize="none"
        />

        {loginError ? <Text style={styles.errorText}>{loginError}</Text> : null}

        <TouchableOpacity style={styles.button} onPress={handleLogin}>
          <Text style={styles.buttonText}>Ingresar</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f3e8ff',
    padding: 20,
  },
  card: {
    width: '100%',
    maxWidth: 420,
    backgroundColor: '#fff',
    padding: 28,
    borderRadius: 16,
    shadowColor: '#000',
    shadowOpacity: 0.12,
    shadowRadius: 16,
    elevation: 10,
    alignItems: 'center',
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#6b21a8',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 14,
    color: '#555',
    marginBottom: 24,
    textAlign: 'center',
  },
  input: {
    width: '100%',
    height: 48,
    borderColor: '#d1d5db',
    borderWidth: 1,
    borderRadius: 10,
    marginBottom: 18,
    paddingHorizontal: 14,
    backgroundColor: '#fafafa',
    color: '#000',
  },
  errorText: {
    color: '#dc2626',
    marginBottom: 16,
    textAlign: 'center',
  },
  button: {
    width: '100%',
    height: 48,
    borderRadius: 10,
    backgroundColor: '#6b21a8',
    justifyContent: 'center',
    alignItems: 'center',
  },
  buttonText: {
    color: '#fff',
    fontWeight: '700',
    fontSize: 16,
  },
});
