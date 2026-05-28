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
    SpaceMono: require('../assets/fonts/SpaceMono-Regular.ttf'),
    ...FontAwesome.font,
  });

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

  return <RootLayoutNav />;
}

function RootLayoutNav() {
  const colorScheme = useColorScheme();

  // 🔐 ESTADO PARA EL LOCK WEB (Solo pide contraseña)
  // Si es Android, inicia en true (pasa directo). Si es Web, inicia bloqueado (false).
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(Platform.OS !== 'web');
  const [password, setPassword] = useState<string>('');
  const [loginError, setLoginError] = useState<string>('');

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
      console.error("Error en el flujo de verificación de versión móvil:", err);
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

  const handleWebLogin = () => {
    // Lee la contraseña segura inyectada desde el panel de Vercel
    const claveSegura = process.env.EXPO_PUBLIC_WEB_PASSWORD;

    if (password === claveSegura) {
      setIsAuthenticated(true);
    } else {
      setLoginError("Contraseña incorrecta para el acceso Web.");
      setPassword('');
    }
  };

  // 🧱 INTERCEPCIÓN WEB: Si es entorno web y no puso la clave, renderiza este formulario de bloqueo
  if (!isAuthenticated) {
    return (
      <View style={styles.container}>
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
            onSubmitEditing={handleWebLogin} // Permite ingresar apretando 'Enter' en el teclado
          />
          
          {loginError ? <Text style={styles.errorText}>{loginError}</Text> : null}
          
          <TouchableOpacity style={styles.button} onPress={handleWebLogin}>
            <Text style={styles.buttonText}>Acceder al Sistema</Text>
          </TouchableOpacity>
        </View>
      </View>
    );
  }

  // SI PASA EL ACCESO (O ES ENTORNO ANDROID): Retorna la navegación de pestañas original
  return (
    <ThemeProvider value={colorScheme === 'dark' ? DarkTheme : DefaultTheme}>
      <Stack>
        <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
        <Stack.Screen name="modal" options={{ presentation: 'modal' }} />
      </Stack>
    </ThemeProvider>
  );
}

// 🎨 ESTILOS PARA EL FORMULARIO WEB
const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#f3e8ff' },
  card: { width: '90%', maxWidth: 400, backgroundColor: '#fff', padding: 30, borderRadius: 12, shadowColor: '#000', shadowOpacity: 0.1, shadowRadius: 10, elevation: 5, alignItems: 'center' },
  title: { fontSize: 26, fontWeight: 'bold', color: '#6b21a8', marginBottom: 5 },
  subtitle: { fontSize: 14, color: '#666', marginBottom: 25 },
  input: { width: '100%', height: 45, borderColor: '#ccc', borderWidth: 1, borderRadius: 6, marginBottom: 15, paddingHorizontal: 12, backgroundColor: '#fafafa', color: '#000', textAlign: 'center' },
  errorText: { color: '#dc2626', marginBottom: 15, fontSize: 14, fontWeight: '500', textAlign: 'center' },
  button: { width: '100%', backgroundColor: '#6b21a8', height: 45, borderRadius: 6, justifyContent: 'center', alignItems: 'center' },
  buttonText: { color: '#fff', fontWeight: 'bold', fontSize: 16 }
});