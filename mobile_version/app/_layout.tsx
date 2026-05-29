import FontAwesome from '@expo/vector-icons/FontAwesome';
import { DarkTheme, DefaultTheme, ThemeProvider } from '@react-navigation/native';
import { useFonts } from 'expo-font';
import { Stack, usePathname, useRouter } from 'expo-router';
import * as SplashScreen from 'expo-splash-screen';
import { createContext, useContext, useEffect, useMemo, useState } from 'react';
import { Alert, Platform } from 'react-native';
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
  const router = useRouter();
  
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

  const pathname = usePathname();

  // 🛡️ GUARDIÁN DE RUTAS INTERNO
  useEffect(() => {
    if (Platform.OS !== 'web') return;

    const routeIsLogin = pathname === '/login';

    if (!isAuthenticated && !routeIsLogin) {
      router.replace('/login');
      return;
    }

    if (isAuthenticated && routeIsLogin) {
      router.replace('/');
    }
  }, [isAuthenticated, pathname, router]);

  if (!loaded) {
    return null;
  }

  if (isWeb && !isAuthenticated && pathname !== '/login') {
    return null;
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

  // 💥 FILTRO AGRESIVO EN EL ENRUTADOR:
  // Si está en la Web y no está autenticado, las pestañas '(tabs)' directamente NO SE DEFINEN en el Stack.
  return (
    <Stack initialRouteName={isWeb ? 'login' : '(tabs)'}>
      <Stack.Screen name="login" options={{ headerShown: false }} />
      
      {(!isWeb || isAuthenticated) && (
        <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
      )}
      
      <Stack.Screen name="modal" options={{ presentation: 'modal' }} />
    </Stack>
  );
}