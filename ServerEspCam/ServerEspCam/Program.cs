using System;
using System.Collections.Generic;
using System.Data;
using System.Data.SqlClient;
using System.Linq;
using System.Net.Mail;
using System.Text;
using System.Threading.Tasks;
using System.Xml.Linq;
using Npgsql;
using uPLibrary.Networking.M2Mqtt;
using uPLibrary.Networking.M2Mqtt.Messages;
using SendGrid;
using SendGrid.Helpers.Mail;


namespace ServerEspCam
{
    internal class Program
    {
        static void Main(string[] args)
        {
            MqttClient mqtt = new MqttClient("test.mosquitto.org");
            mqtt.Connect("8402d29a-e588-4567-b887-947785a1b8ce");
            string[] subscribe = new string[1];
            subscribe[0] = "Esp32_FaceWebServer_SQL";

            mqtt.MqttMsgPublishReceived += MqttClient_MqttMsgPublishReceived;
            byte[] bytes = new byte[1];

            mqtt.Subscribe(subscribe, new byte[] { MqttMsgBase.QOS_LEVEL_AT_LEAST_ONCE });
            
            while (mqtt.IsConnected)
            {
                

            }

            TestConnection();
        }

        private static void ReturnEmail()
        {
            using (NpgsqlConnection connection = GetConnection())
            {
                string query = "SELECT name, email FROM public.iotespcam WHERE ADM = TRUE;";
                using (NpgsqlCommand command = new NpgsqlCommand(query, connection))
                {
                    connection.Open();
                    using (NpgsqlDataReader reader = command.ExecuteReader())
                    {
                        MqttClient mqtt2 = new MqttClient("test.mosquitto.org");
                        mqtt2.Connect("8402d29a-e588-4567-b687-947785a1b8ce");
                        while (reader.Read())
                        {
                            string email = reader.GetString(0) +";" + reader.GetString(1);
                            byte[] bytes = Encoding.UTF8.GetBytes(email);
                            mqtt2.Publish("Esp32_FaceWebServer_EMAIL", bytes);
                            Console.WriteLine(email);
                        }
                    }
                }
            }
        }
        private static void InsertSql(string Message)
        {
            using(NpgsqlConnection connection = GetConnection())
            {
                connection.Open();

                string[] insertData = Message.Split(';');
                if (insertData.Length > 2)
                {
                    string query = "INSERT INTO public.iotespcam(name, email, adm) VALUES (@Name," +
                        " @Email," + "@ADM);";

                    using (NpgsqlCommand command = new NpgsqlCommand(query, connection))
                    {
                        Console.WriteLine(insertData[0]);
                        command.Parameters.AddWithValue("@Name", insertData[0]);
                        Console.WriteLine(insertData[1]);
                        command.Parameters.AddWithValue("@Email", insertData[1]);
                        if (insertData[2] == "0")
                        {

                            command.Parameters.AddWithValue("@ADM", false);
                        }
                        else
                        {
                            command.Parameters.AddWithValue("@ADM", true);

                        }
                        Console.WriteLine("Dados salvos no banco de dados com sucesso!");
                        command.ExecuteNonQuery();
                    }
                    Console.WriteLine("Email de Verificação enviado com sucesso!");
                    Console.WriteLine();
                }
            }
        }
        private static void TestConnection()
        {
            using (NpgsqlConnection connection = GetConnection())
            {
                    try
                    {
                        connection.Open();
                        if (connection.State == ConnectionState.Open)
                        {
                            Console.WriteLine("Connected");
                        }
                    }
                    catch
                    {
                        Console.WriteLine("Not Connected");
                    }
                }
            }
        private static NpgsqlConnection GetConnection()
        {
            return new NpgsqlConnection(@"Server=localhost;Port=5432;User Id=postgres;Password=2510;Database=IotEspCam");
        }

        private static void MqttClient_MqttMsgPublishReceived(object sender, uPLibrary.Networking.M2Mqtt.Messages.MqttMsgPublishEventArgs e)
        {
            var message = Encoding.UTF8.GetString(e.Message);
            Console.WriteLine(message);
            if(message != "email")
            {
                InsertSql(message);
            }
            else 
            {
                ReturnEmail();
            }
        }

    }

}
