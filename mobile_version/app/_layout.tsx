import FontAwesome from '@expo/vector-icons/FontAwesome';
import { DarkTheme, DefaultTheme, ThemeProvider } from '@react-navigation/native';
import { useFonts } from 'expo-font';
import { Stack } from 'expo-router';
import * as SplashScreen from 'expo-splash-screen';
import { createContext, useContext, useEffect, useMemo, useState } from 'react';
import { Alert, Platform, Pressable, StyleSheet, Text, TextInput, View } from 'react-native';
import 'react-native-reanimated';

// Importamos las librerías nativas para manejar la actualización
import * as Application from 'expo-application';
import * as IntentLauncher from 'expo-intent-launcher';

// Truco final de TypeScript
import ExpoFileSystem from 'expo-file-system';
const FileSystem: any = ExpoFileSystem;

// Importamos tu cliente de API modificado
import { ApiClient } from '../api/api_client'; 
import { useColorScheme } from '@/components/useColorScheme';

export {
  ErrorBoundary,
} from 'expo-router';

const isWeb = Platform.OS === 'web';

export const unstable_settings = {
  initialRouteName: isWeb ? 'login' : '(tabs)',
};

SplashScreen.preventAutoHideAsync();

const AuthContext = createContext<{
  isAuthenticated: boolean;
  setIsAuthenticated: React.Dispatch<React.SetStateAction<boolean>>;
} | null>(null);

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth debe usarse dentro de AuthContext');
  }
  return context;
}

export default function RootLayout() {
  // ✅ ADIÓS COMPILACIONES FALLIDAS: Sacamos el require del .ttf que rompía Metro
  const [loaded, error] = useFonts({
    ...FontAwesome.font,
  });

  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(Platform.OS !== 'web');

  useEffect(() => {
    if (error) throw error;
  }, [error]);

  useEffect(() => {
    if (loaded) {
      SplashScreen.hideAsync();
    }
  }, [loaded]);

  if (!loaded) {
    return null;
  }

  if (isWeb && !isAuthenticated) {
    return <WebLoginScreen onAuthenticated={() => setIsAuthenticated(true)} />;
  }

  const authContextValue = useMemo(
    () => ({ isAuthenticated, setIsAuthenticated }),
    [isAuthenticated]
  );

  return (
    <AuthContext.Provider value={authContextValue}>
      <ThemeProvider value={useColorScheme() === 'dark' ? DarkTheme : DefaultTheme}>
        <RootLayoutNav isAuthenticated={isAuthenticated} />
      </ThemeProvider>
    </AuthContext.Provider>
  );
}

function RootLayoutNav({ isAuthenticated }: { isAuthenticated: boolean }) {
  // 🚀 LÓGICA DE AUTO-UPDATE INTEGRADA (Solo Android)
  useEffect(() => {
    if (Platform.OS === 'android') {
      ejecutarChequeoDeVersion();
    }
  }, []);

  const ejecutarChequeoDeVersion = async () => {
    try {
      const versionActual = Application.nativeApplicationVersion;
      const datosServidor = await ApiClient.checkMobileVersion();
      if (!datosServidor) return;

      const { latestVersion, downloadUrl } = datosServidor;

      if (versionActual !== latestVersion && downloadUrl) {
        Alert.alert(
          "¡Nueva versión disponible!",
          `Hay una actualización disponible (v${latestVersion}). ¿Querés instalarla ahora para tener las últimas mejoras?`,
          [
            { text: "Más tarde", style: "cancel" },
            { text: "Actualizar", onPress: () => descargarEInstalarApk(downloadUrl) }
          ]
        );
      }
    } catch (err) {
      console.error("Error en el flujo de verificación de velocidad móvil:", err);
    }
  };

  const descargarEInstalarApk = async (urlDeGitHub: string) => {
    try {
      Alert.alert("Descargando", "La actualización se está bajando desde GitHub, aguarda un momento...");
      const nombreArchivo = "renuevo_update.apk";
      const rutaDestino = `${FileSystem.cacheDirectory}${nombreArchivo}`;
      const resultadoDescarga = await FileSystem.downloadAsync(urlDeGitHub, rutaDestino);

      if (resultadoDescarga.status === 200) {
        const contentUri = await FileSystem.getContentUriAsync(resultadoDescarga.uri);
        await IntentLauncher.startActivityAsync('android.intent.action.INSTALL_PACKAGE', {
          data: contentUri,
          flags: 1,
          type: 'application/vnd.android.package-archive'
        });
      } else {
        Alert.alert("Error de descarga", "No se pudo obtener el archivo desde GitHub.");
      }
    } catch (error) {
      console.error("Error al intentar instalar el APK:", error);
      Alert.alert("Error de installation", "Hubo un problema al instalar.");
    }
  };

  return (
    <Stack initialRouteName="(tabs)">
      <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
      <Stack.Screen name="modal" options={{ presentation: 'modal' }} />
    </Stack>
  );
}

function WebLoginScreen({
  onAuthenticated,
}: {
  onAuthenticated: () => void;
}) {
  const [password, setPassword] = useState('');
  const [loginError, setLoginError] = useState('');
  const [statusMessage, setStatusMessage] = useState('');

  const handleLogin = () => {
    const claveSegura = process.env.EXPO_PUBLIC_WEB_PASSWORD;

    if (!claveSegura) {
      setLoginError('Error de configuración: falta la contraseña de acceso web.');
      setStatusMessage('');
      setPassword('');
      return;
    }

    if (password.trim() === claveSegura) {
      setStatusMessage('Contraseña correcta. Cargando...');
      setLoginError('');
      setPassword('');
      onAuthenticated();
    } else {
      setLoginError('Contraseña incorrecta para el acceso Web.');
      setStatusMessage('');
      setPassword('');
    }
  };

  return (
    <View style={webLoginStyles.container}>
      <View style={webLoginStyles.card}>
        <Text style={webLoginStyles.title}>Renuevo Church</Text>
        <Text style={webLoginStyles.subtitle}>Acceso Web Interno</Text>

        <TextInput
          placeholder="Contraseña"
          placeholderTextColor="#999"
          value={password}
          onChangeText={setPassword}
          style={webLoginStyles.input}
          onSubmitEditing={handleLogin}
          autoCapitalize="none"
          autoComplete="off"
          autoCorrect={false}
          textContentType="none"
        />

        {loginError ? <Text style={webLoginStyles.errorText}>{loginError}</Text> : null}
        {statusMessage ? <Text style={webLoginStyles.statusText}>{statusMessage}</Text> : null}

        <Pressable style={webLoginStyles.button} onPress={handleLogin}>
          <Text style={webLoginStyles.buttonText}>Ingresar</Text>
        </Pressable>
      </View>
    </View>
  );
}

const webLoginStyles = StyleSheet.create({
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
  statusText: {
    color: '#444',
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