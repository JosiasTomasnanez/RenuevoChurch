import FontAwesome from '@expo/vector-icons/FontAwesome';
import { DarkTheme, DefaultTheme, ThemeProvider } from '@react-navigation/native';
import { useFonts } from 'expo-font';
import { Stack } from 'expo-router';
import * as SplashScreen from 'expo-splash-screen';
import { useEffect, useState } from 'react'; 
import { Alert, Platform, View, Text, TextInput, TouchableOpacity, StyleSheet } from 'react-native'; 
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

export const unstable_settings = {
  initialRouteName: '(tabs)',
};

SplashScreen.preventAutoHideAsync();

export default function RootLayout() {
  const [loaded, error] = useFonts({
    SpaceMono: require('../../assets/fonts/SpaceMono-Regular.ttf'), // Ajustado por si acaso la ruta relativa fallaba
    ...FontAwesome.font,
  });

  // 🔐 EL CANDADO SE MUEVE AL COMPONENTE PADRE
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(Platform.OS !== 'web');
  const [authReady, setAuthReady] = useState<boolean>(Platform.OS !== 'web');
  const [password, setPassword] = useState<string>('');
  const [loginError, setLoginError] = useState<string>('');

  useEffect(() => {
    if (error) throw error;
  }, [error]);

  useEffect(() => {
    if (Platform.OS === 'web') {
      const savedAuth = window.localStorage.getItem('RENUEVO_WEB_AUTH');
      if (savedAuth === 'ok') {
        setIsAuthenticated(true);
      }
      setAuthReady(true);
    }
  }, []);

  useEffect(() => {
    if (loaded && authReady) {
      // Solo ocultamos el splash screen si ya pasó el login web (o si es Android)
      if (isAuthenticated || Platform.OS !== 'web') {
        SplashScreen.hideAsync();
      }
    }
  }, [loaded, authReady, isAuthenticated]);

  if (!loaded || (Platform.OS === 'web' && !authReady)) {
    return null;
  }

  const handleWebLogin = () => {
    const claveSegura = process.env.EXPO_PUBLIC_WEB_PASSWORD;

    if (!claveSegura) {
      setLoginError('Error de configuración: falta la contraseña de acceso web.');
      setPassword('');
      return;
    }

    if (password.trim() === claveSegura) {
      window.localStorage.setItem('RENUEVO_WEB_AUTH', 'ok');
      setIsAuthenticated(true);
      setLoginError('');
      setPassword('');
    } else {
      setLoginError('Contraseña incorrecta para el acceso Web.');
      setPassword('');
    }
  };

  // 💥 CORTE RADICAL: Si es Web y no está autenticado, mostramos el login AQUÍ MISMO.
  // Al retornar esto acá, "<RootLayoutNav />" NUNCA se ejecuta, por ende Expo Router está totalmente muerto.
  if (Platform.OS === 'web' && !isAuthenticated) {
    return (
      <View style={styles.webAbsoluteLock}>
        <View style={styles.card}>
          <Text style={styles.title}>Renuevo Church</Text>
          <Text style={styles.subtitle}>Gestión Interna - Acceso Web</Text>
          
          <TextInput 
            placeholder="Introduce la contraseña de la iglesia" 
            placeholderTextColor="#999"
            secureTextEntry 
            value={password} 
            onChangeText={setPassword} 
            style={styles.input}
            onSubmitEditing={handleWebLogin}
          />
          
          {loginError ? <Text style={styles.errorText}>{loginError}</Text> : null}
          
          <TouchableOpacity style={styles.button} onPress={handleWebLogin}>
            <Text style={styles.buttonText}>Acceder al Sistema</Text>
          </TouchableOpacity>
        </View>
      </View>
    );
  }

  // Si es Android, o si ya puso la contraseña en la Web, recién ahí dejamos que cargue el resto
  return <RootLayoutNav />;
}

function RootLayoutNav() {
  const colorScheme = useColorScheme();

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
    <ThemeProvider value={colorScheme === 'dark' ? DarkTheme : DefaultTheme}>
      <Stack>
        <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
        <Stack.Screen name="modal" options={{ presentation: 'modal' }} />
      </Stack>
    </ThemeProvider>
  );
}

// 🎨 ESTILOS MÁXIMA AGRESIVIDAD
const styles = StyleSheet.create({
  webAbsoluteLock: { 
    position: 'fixed',
    top: 0,
    left: 0,
    width: '100vw' as any,
    height: '100vh' as any,
    justifyContent: 'center', 
    alignItems: 'center', 
    backgroundColor: '#f3e8ff',
    zIndex: 9999999,
  },
  card: { width: '90%', maxWidth: 400, backgroundColor: '#fff', padding: 30, borderRadius: 12, shadowColor: '#000', shadowOpacity: 0.1, shadowRadius: 10, elevation: 5, alignItems: 'center' },
  title: { fontSize: 26, fontWeight: 'bold', color: '#6b21a8', marginBottom: 5 },
  subtitle: { fontSize: 14, color: '#666', marginBottom: 25 },
  input: { width: '100%', height: 45, borderColor: '#ccc', borderWidth: 1, borderRadius: 6, marginBottom: 15, paddingHorizontal: 12, backgroundColor: '#fafafa', color: '#000', textAlign: 'center' },
  errorText: { color: '#dc2626', marginBottom: 15, fontSize: 14, fontWeight: '500', textAlign: 'center' },
  button: { width: '100%', backgroundColor: '#6b21a8', height: 45, borderRadius: 6, justifyContent: 'center', alignItems: 'center' },
  buttonText: { color: '#fff', fontWeight: 'bold', fontSize: 16 }
});